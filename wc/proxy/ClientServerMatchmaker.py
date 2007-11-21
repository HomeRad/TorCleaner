# -*- coding: iso-8859-1 -*-
# Copyright (c) 2000, Amit Patel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of Amit Patel nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Mediator between client and server connection objects.
"""

import socket
import cStringIO as StringIO

import wc.log
import wc.configuration
import wc.url
import dns_lookups
import ServerHandleDirectly
import HttpServer
from ServerPool import serverpool


BUSY_LIMIT = 10


class ClientServerMatchmaker (object):
    """
    The Matchmaker waits until the server connection is established
    and a response was received from it. Then it matches the client
    and server connections together.

    States:
      - dns
        Client has sent all of the browser information
        We have asked for a DNS lookup
        We are waiting for an IP address
        =>  Either we get an IP address, we redirect, or we fail
      - server
        We have an IP address
        We are looking for a suitable server
        =>  Either we find a server from ServerPool and use it
        (go into 'response'), or we create a new server
        (go into 'connect'), or we wait a bit (stay in 'server')
      - connect
        We have a brand new server object
        We are waiting for it to connect
        =>  Either it connects and we send the request (go into
        'response'), or it fails and we notify the client
      - response
        We have sent a request to the server
        We are waiting for it to respond
        =>  Either it responds and we have a client/server match
        (go into 'done'), it doesn't and we retry (go into
        'server'), or it doesn't and we give up (go into 'done')
      - done
        We are done matching up the client and server
    """

    def __init__ (self, client, request, headers, content,
                  mime_types=None, sslserver=False):
        """
        If mime is not None, the response will have the specified
        mime type, regardless of the Content-Type header value.
        This is useful for JavaScript fetching and blocked pages.
        """
        self.do_ssl = wc.HasSsl and wc.configuration.config['sslgateway']
        self.sslserver = sslserver
        self.client = client
        self.localhost = client.localhost
        self.request = request
        self.headers = headers
        self.content = content
        if mime_types is None:
            self.mime_types = []
        else:
            self.mime_types = mime_types
        self.state = 'dns'
        self.server_busy = 0
        self.method, self.url, self.protocol = self.request.split()
        # prepare DNS lookup
        if wc.configuration.config['parentproxy']:
            self.hostname = wc.configuration.config['parentproxy']
            self.port = wc.configuration.config['parentproxyport']
            self.document = self.url
            if wc.configuration.config['parentproxycreds']:
                auth = wc.configuration.config['parentproxycreds']
                self.headers['Proxy-Authorization'] = "%s\r" % auth
        else:
            if self.do_ssl and self.method == 'CONNECT':
                # delegate to SSL gateway
                self.hostname = 'localhost'
                self.port = wc.configuration.config['sslport']
            else:
                self.hostname = client.hostname
                self.port = client.port
            self.document = client.document
        assert self.hostname
        # start DNS lookup
        assert None == wc.log.debug(wc.LOG_PROXY,
                            "background dns lookup %r", self.hostname)
        dns_lookups.background_lookup(self.hostname, self.handle_dns)

    def get_ip_addr (self):
        ip = self.try_addrs[0]
        del self.try_addrs[0]
        return ip

    def handle_dns (self, hostname, answer):
        """
        Got dns answer, look for server.
        """
        assert self.state == 'dns'
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s handle dns %r", self, hostname)
        if not self.client.connected:
            wc.log.info(wc.LOG_PROXY, "%s client closed after DNS", self)
            # The browser has already closed this connection, so abort
            return
        if answer.isFound():
            # The data is a list of strings resembling IP addresses.
            # Be sure not to copy the list since it is modified.
            self.ipaddrs = answer.data
            # A copy if IP addresses to keep track what IPs have been tried.
            self.try_addrs = self.ipaddrs[:]
            # Try the first IP in the list.
            self.ipaddr = self.get_ip_addr()
            self.state = 'server'
            self.find_server()
        elif answer.isRedirect():
            # Let's use a different hostname
            new_url = self.client.scheme+"://"+answer.data
            if self.port != 80:
                new_url += ':%d' % self.port
            # XXX does not work with parent proxy
            new_url += self.document
            wc.log.info(wc.LOG_PROXY, "%s redirecting %r", self, new_url)
            self.state = 'done'
            ServerHandleDirectly.ServerHandleDirectly(
              self.client,
              '%s 301 Moved Permanently' % self.protocol, 301,
              wc.http.header.WcMessage(
                    StringIO.StringIO('Content-type: text/plain\r\n'
                                      'Location: %s\r\n\r\n' % new_url)),
               _('Host %s is an abbreviation for %s')%(hostname, answer.data))
        else:
            # Couldn't look up the host,
            # close this connection
            self.state = 'done'
            self.client.error(504, _("Host not found"),
                _('Host %s not found .. %s')%(hostname, answer.data))

    def find_server (self):
        """
        Search for a connected server or make a new one.
        """
        assert self.state == 'server'
        addr = (self.ipaddr, self.port)
        # XXX why do I have to import wc again - python bug?
        import wc
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s find server %s", self, addr)
        if not self.client.connected:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s client not connected", self)
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # Let's reuse it
            assert None == wc.log.debug(wc.LOG_PROXY,
                                '%s resurrecting %s', self, server)
            self.state = 'connect'
            self.server_connected(server)
        elif serverpool.count_servers(addr) >= \
             serverpool.connection_limit(addr):
            assert None == wc.log.debug(wc.LOG_PROXY,
                '%s server %s busy', self, addr)
            self.server_busy += 1
            # if we waited too long for a server to be available, abort
            if self.server_busy > BUSY_LIMIT:
                wc.log.info(wc.LOG_PROXY,
                    "Waited too long for available connection at %s" \
                    ", consider increasing the server pool connection limit" \
                    " (currently at %d)", addr, BUSY_LIMIT)
                self.client.error(503, _("Service unavailable"))
                return
            # There are too many connections right now, so register us
            # as an interested party for getting a connection later
            serverpool.register_callback(addr, self.find_server)
        else:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s new connect to server", self)
            # Let's make a new one
            self.state = 'connect'
            # note: all Server objects eventually call server_connected
            try:
                if self.do_ssl and self.sslserver:
                    import SslServer
                    klass = SslServer.SslServer
                else:
                    klass = HttpServer.HttpServer
                server = klass(self.ipaddr, self.port, self)
                serverpool.register_server(addr, server)
            except socket.error:
                self.client.error(503, _('Connect error'))

    def server_connected (self, server):
        """
        The server has connected.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s server_connected", self)
        assert self.state == 'connect'
        assert server.connected
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.client_abort()
            return
        if self.method == 'CONNECT':
            self.state = 'response'
            headers = wc.http.header.WcMessage()
            self.server_response(server, 'HTTP/1.1 200 OK', 200, headers)
            if wc.configuration.config['sslgateway']:
                server.client_send_request(self.method, self.protocol,
                                   self.hostname, self.port,
                                   self.document, self.headers,
                                   self.content, self,
                                   self.url, self.mime_types)
                server.client = self.client
            return
        # check expectations
        addr = (self.ipaddr, self.port)
        expect = self.headers.get('Expect', '').lower().strip()
        docontinue = expect.startswith('100-continue') or \
                     expect.startswith('0100-continue')
        if docontinue:
            if serverpool.http_versions.get(addr, 1.1) < 1.1:
                self.client.error(417, _("Expectation failed"),
                             _("Server does not understand HTTP/1.1"))
                return
        elif expect:
            self.client.error(417, _("Expectation failed"),
                       _("Unsupported expectation %r")%expect)
            return
        # switch to response status
        self.state = 'response'
        # At this point, we tell the server that we are the client.
        # Once we get a response, we transfer to the real client.
        server.client_send_request(self.method, self.protocol,
                                   self.hostname, self.port,
                                   self.document, self.headers,
                                   self.content, self,
                                   self.url, self.mime_types)

    def server_abort (self, reason=_("No response from server")):
        """
        The server had an error, so we need to tell the client
        that we couldn't connect, or try another IP of the DNS IP list
        to connect to.
        """
        if self.client.connected:
            if self.try_addrs:
                # There are still IP addresses to try out.
                # Shuffle the failed IP to the end if the DNS list for
                # subsequent requests.
                del self.ipaddrs[0]
                self.ipaddrs.append(self.ipaddr)
                # Get the next IP address in the list.
                self.ipaddr = self.get_ip_addr()
                wc.log.info(wc.LOG_PROXY, "%s try next IP %s",
                            self, self.ipaddr)
                self.state = "server"
                self.find_server()
            else:
                # Tell the client that the server had an error.
                self.client.error(503, reason)

    def server_close (self, server):
        """
        The server has closed.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            '%s resurrection failed %d %s',
            self, server.sequence_number, server)
        # Look for a server again
        if server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection. Let's find another server object.
            self.state = 'server'
            self.find_server()
        elif self.client.connected:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            self.client.error(503, _("Server did not respond"))

    def server_response (self, server, response, status, headers):
        """
        The server got a response.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s server_response, match client/server", self)
        # Okay, transfer control over to the real client
        if self.client.connected:
            server.client = self.client
            self.client.server_response(server, response, status, headers)
        else:
            server.client_abort()

    def __repr__ (self):
        """
        Object representation.
        """
        if self.client:
            extra = "client"
        else:
            extra = ""
        extra += " "+self.url
        return '<%s:%-8s %s>' % ('clientserver', self.state, extra)
