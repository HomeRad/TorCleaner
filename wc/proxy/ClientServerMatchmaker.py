# -*- coding: iso-8859-1 -*-
"""Mediator between client and server connection objects"""

import socket
import cStringIO as StringIO
import bk.i18n
import bk.url
import wc
import wc.proxy.dns_lookups
import wc.proxy.Headers
from wc.proxy.ServerPool import serverpool
import wc.proxy.ServerHandleDirectly
import wc.proxy.HttpServer
import wc.proxy.SslServer


BUSY_LIMIT = 10


class ClientServerMatchmaker (object):
    """ The Matchmaker waits until the server connection is established
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

    def __init__ (self, client, request, headers, content, mime=None):
        """if mime is not None, the response will have the specified
           mime type, regardless of the Content-Type header value.
           This is useful for JavaScript fetching and blocked pages.
        """
        self.client = client
        self.request = request
        self.headers = headers
        self.content = content
        self.mime = mime
        self.state = 'dns'
        self.server_busy = 0
        self.method, self.url, self.protocol = self.request.split()
        # prepare DNS lookup
        if wc.config['parentproxy']:
            self.hostname = wc.config['parentproxy']
            self.port = wc.config['parentproxyport']
            self.document = self.url
            if wc.config['parentproxycreds']:
                auth = wc.config['parentproxycreds']
                self.headers['Proxy-Authorization'] = "%s\r"%auth
        else:
            if self.method=='CONNECT' and wc.config['sslgateway']:
                # delegate to SSL gateway
                self.hostname = 'localhost'
                self.port = wc.config['sslport']
            else:
                self.hostname = client.hostname
                self.port = client.port
            self.document = bk.url.document_quote(client.document)
        assert self.hostname
        # start DNS lookup
        bk.log.debug(wc.LOG_PROXY, "background dns lookup %r", self.hostname)
        wc.proxy.dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_dns (self, hostname, answer):
        """got dns answer, look for server"""
        assert self.state == 'dns'
        bk.log.debug(wc.LOG_PROXY, "%s handle dns %r", self, hostname)
        if not self.client.connected:
            bk.log.warn(wc.LOG_PROXY, "%s client closed after DNS", self)
            # The browser has already closed this connection, so abort
            return
        if answer.isFound():
            self.ipaddr = answer.data[0]
	    self.state = 'server'
            self.find_server()
        elif answer.isRedirect():
            # Let's use a different hostname
            new_url = self.client.scheme+"://"+answer.data
            if self.port != 80:
	        new_url += ':%d' % self.port
            # XXX does not work with parent proxy
            new_url += self.document
            bk.log.info(wc.LOG_PROXY, "%s redirecting %r", self, new_url)
            self.state = 'done'
            wc.proxy.ServerHandleDirectly.ServerHandleDirectly(
              self.client,
              '%s 301 Moved Permanently' % self.protocol, 301,
              wc.proxy.Headers.WcMessage(StringIO.StringIO('Content-type: text/plain\r\n'
              'Location: %s\r\n\r\n' % new_url)),
              bk.i18n._('Host %s is an abbreviation for %s')%(hostname, answer.data))
        else:
            # Couldn't look up the host,
            # close this connection
            self.state = 'done'
            self.client.error(504, bk.i18n._("Host not found"),
                bk.i18n._('Host %s not found .. %s')%(hostname, answer.data))


    def find_server (self):
        """search for a connected server or make a new one"""
        assert self.state == 'server'
        addr = (self.ipaddr, self.port)
        bk.log.debug(wc.LOG_PROXY, "%s find server %s", self, addr)
        if not self.client.connected:
            bk.log.debug(wc.LOG_PROXY, "%s client not connected", self)
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # Let's reuse it
            bk.log.debug(wc.LOG_PROXY, '%s resurrecting %s', self, server)
            self.state = 'connect'
            self.server_connected(server)
        elif serverpool.count_servers(addr) >= \
             serverpool.connection_limit(addr):
            bk.log.debug(wc.LOG_PROXY, '%s server %s busy', self, addr)
            self.server_busy += 1
            # if we waited too long for a server to be available, abort
            if self.server_busy > BUSY_LIMIT:
                bk.log.warn(wc.LOG_PROXY, "Waited too long for available connection at %s"+\
                    ", consider increasing the server pool connection limit"+\
                     " (currently at %d)", addr, BUSY_LIMIT)
                self.client.error(503, bk.i18n._("Service unavailable"))
                return
            # There are too many connections right now, so register us
            # as an interested party for getting a connection later
            serverpool.register_callback(addr, self.find_server)
        else:
            bk.log.debug(wc.LOG_PROXY, "%s new connect to server", self)
            # Let's make a new one
            self.state = 'connect'
            # note: all Server objects eventually call server_connected
            try:
                if self.url.startswith("https://") and wc.config['sslgateway']:
                    klass = wc.proxy.SslServer.SslServer
                else:
                    klass = wc.proxy.HttpServer.HttpServer
                server = klass(self.ipaddr, self.port, self)
                serverpool.register_server(addr, server)
            except socket.timeout:
                self.client.error(504, bk.i18n._('Connection timeout'))
            except socket.error:
                self.client.error(503, bk.i18n._('Connect error'))


    def server_connected (self, server):
        """the server has connected"""
        bk.log.debug(wc.LOG_PROXY, "%s server_connected", self)
        assert self.state=='connect'
        assert server.connected
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.client_abort()
            return
        if self.method=='CONNECT':
            self.state = 'response'
            headers = wc.proxy.Headers.WcMessage()
            self.server_response(server, 'HTTP/1.1 200 OK', 200, headers)
            if wc.config['sslgateway']:
                server.client_send_request(self.method, self.protocol,
                                   self.hostname, self.port,
                                   self.document, self.headers,
                                   self.content, self,
                                   self.url, self.mime)
                server.client = self.client
            return
        # check expectations
        addr = (self.ipaddr, self.port)
        expect = self.headers.get('Expect', '').lower().strip()
        docontinue = expect.startswith('100-continue') or \
                     expect.startswith('0100-continue')
        if docontinue:
            if serverpool.http_versions.get(addr, 1.1) < 1.1:
                self.client.error(417, bk.i18n._("Expectation failed"),
                             bk.i18n._("Server does not understand HTTP/1.1"))
                return
        elif expect:
            self.client.error(417, bk.i18n._("Expectation failed"),
                       bk.i18n._("Unsupported expectation %r")%expect)
            return
        # switch to response status
        self.state = 'response'
        # At this point, we tell the server that we are the client.
        # Once we get a response, we transfer to the real client.
        server.client_send_request(self.method, self.protocol,
                                   self.hostname, self.port,
                                   self.document, self.headers,
                                   self.content, self,
                                   self.url, self.mime)


    def server_abort (self, reason=bk.i18n._("No response from server")):
        """The server had an error, so we need to tell the client
           that we couldn't connect"""
        if self.client.connected:
            self.client.error(503, reason)


    def server_close (self, server):
        """the server has closed"""
        bk.log.debug(wc.LOG_PROXY, '%s resurrection failed %d %s', self, server.sequence_number, server)
        # Look for a server again
        if server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection. Let's find another server object.
            self.state = 'server'
            self.find_server()
        elif self.client.connected:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            self.client.error(503, bk.i18n._("Server closed connection"))


    def server_response (self, server, response, status, headers):
        """the server got a response"""
        bk.log.debug(wc.LOG_PROXY, "%s server_response, match client/server", self)
        # Okay, transfer control over to the real client
        if self.client.connected:
            server.client = self.client
            self.client.server_response(server, response, status, headers)
        else:
            server.client_abort()


    def __repr__ (self):
        """object representation"""
        if self.client:
            extra = "client"
        else:
            extra = ""
        extra += " "+self.url
        return '<%s:%-8s %s>' % ('clientserver', self.state, extra)
