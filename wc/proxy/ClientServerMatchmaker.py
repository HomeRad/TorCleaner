# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from cStringIO import StringIO
import dns_lookups
from wc.proxy.Headers import WcMessage
from ServerPool import serverpool
from ServerHandleDirectly import ServerHandleDirectly
from wc import i18n, config
from wc.log import *
from wc.url import document_quote

from HttpServer import HttpServer
from SslServer import SslServer

BUSY_LIMIT = 10

class ClientServerMatchmaker (object):
    """ The Matchmaker waits until the server connection is established
    and a response was received from it. Then it matches the client
    and server connections together.
    .
     States:

     dns:      Client has sent all of the browser information
               We have asked for a DNS lookup
               We are waiting for an IP address
           =>  Either we get an IP address, we redirect, or we fail

     server:   We have an IP address
               We are looking for a suitable server
           =>  Either we find a server from ServerPool and use it
               (go into 'response'), or we create a new server
               (go into 'connect'), or we wait a bit (stay in 'server')

     connect:  We have a brand new server object
               We are waiting for it to connect
           =>  Either it connects and we send the request (go into
               'response'), or it fails and we notify the client

     response: We have sent a request to the server
               We are waiting for it to respond
           =>  Either it responds and we have a client/server match
               (go into 'done'), it doesn't and we retry (go into
               'server'), or it doesn't and we give up (go into 'done')

     done:     We are done matching up the client and server
    """

    def __init__ (self, client, request, headers, content, mime=None):
        self.client = client
        self.request = request
        self.headers = headers
        self.content = content
        self.mime = mime
        self.state = 'dns'
        self.server_busy = 0
        self.method, self.url, self.protocol = self.request.split()
        # prepare DNS lookup
        if config['parentproxy']:
            self.hostname = config['parentproxy']
            self.port = config['parentproxyport']
            self.document = self.url
            if config['parentproxycreds']:
                auth = config['parentproxycreds']
                self.headers['Proxy-Authorization'] = "%s\r"%auth
        else:
            if self.method=='CONNECT' and config['sslgateway']:
                # delegate to SSL gateway
                self.hostname = 'localhost'
                self.port = config['sslport']
            else:
                self.hostname = client.hostname
                self.port = client.port
            self.document = document_quote(client.document)
        assert self.hostname
        # start DNS lookup
        debug(PROXY, "background dns lookup %r", self.hostname)
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_dns (self, hostname, answer):
        assert self.state == 'dns'
        debug(PROXY, "%s handle dns %r", self, hostname)
        if not self.client.connected:
            warn(PROXY, "%s client closed after DNS", self)
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
            info(PROXY, "%s redirecting %r", self, new_url)
            self.state = 'done'
            ServerHandleDirectly(
              self.client,
              '%s 301 Moved Permanently' % self.protocol, 301,
              WcMessage(StringIO('Content-type: text/plain\r\n'
              'Location: %s\r\n\r\n' % new_url)),
              i18n._('Host %s is an abbreviation for %s')%(hostname, answer.data))
        else:
            # Couldn't look up the host,
            # close this connection
            self.state = 'done'
            self.client.error(504, i18n._("Host not found"),
                i18n._('Host %s not found .. %s')%(hostname, answer.data))


    def find_server (self):
        """search for a connected server or make a new one"""
        assert self.state == 'server'
        addr = (self.ipaddr, self.port)
        debug(PROXY, "%s find server %s", self, addr)
        if not self.client.connected:
            debug(PROXY, "%s client not connected", self)
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # Let's reuse it
            debug(PROXY, '%s resurrecting %s', self, server)
            self.state = 'connect'
            self.server_connected(server)
        elif serverpool.count_servers(addr)>=serverpool.connection_limit(addr):
            debug(PROXY, '%s server %s busy', self, addr)
            self.server_busy += 1
            # if we waited too long for a server to be available, abort
            if self.server_busy > BUSY_LIMIT:
                warn(PROXY, "Waited too long for available connection at %s"+\
                    ", consider increasing the server pool connection limit"+\
                     " (currently at %d)", addr, BUSY_LIMIT)
                self.client.error(503, i18n._("Service unavailable"))
                return
            # There are too many connections right now, so register us
            # as an interested party for getting a connection later
            serverpool.register_callback(addr, self.find_server)
        else:
            debug(PROXY, "%s new connect to server", self)
            # Let's make a new one
            self.state = 'connect'
            # note: all Server objects eventually call server_connected
            try:
                if self.url.startswith("https://") and config['sslgateway']:
                    server = SslServer(self.ipaddr, self.port, self)
                else:
                    server = HttpServer(self.ipaddr, self.port, self)
                serverpool.register_server(addr, server)
            except socket.timeout:
                self.client.error(504, i18n._('Connection timeout'))
            except socket.error:
                self.client.error(503, i18n._('Connect error'))


    def server_connected (self, server):
        """the server has connected"""
        debug(PROXY, "%s server_connected", self)
        assert self.state=='connect'
        assert server.connected
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.client_abort()
            return
        if self.method=='CONNECT':
            self.state = 'response'
            headers = WcMessage()
            self.server_response(server, 'HTTP/1.1 200 OK', 200, headers)
            if config['sslgateway']:
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
                self.client.error(417, i18n._("Expectation failed"),
                             i18n._("Server does not understand HTTP/1.1"))
                return
        elif expect:
            self.client.error(417, i18n._("Expectation failed"),
                       i18n._("Unsupported expectation %r")%expect)
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


    def server_abort (self):
        # The server had an error, so we need to tell the client
        # that we couldn't connect
        if self.client.connected:
            self.client.error(503, i18n._("No response from server"))


    def server_close (self, server):
        """the server has closed"""
        debug(PROXY, '%s resurrection failed %d %s', self, server.sequence_number, server)
        # Look for a server again
        if server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection. Let's find another server object.
            self.state = 'server'
            self.find_server()
        elif self.client.connected:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            self.client.error(503, i18n._("Server closed connection"))


    def server_response (self, server, response, status, headers):
        """the server got a response"""
        debug(PROXY, "%s server_response, match client/server", self)
        # Okay, transfer control over to the real client
        if self.client.connected:
            server.client = self.client
            self.client.server_response(server, response, status, headers)
        else:
            server.client_abort()


    def __repr__ (self):
        if self.client:
            extra = "client"
        else:
            extra = ""
        extra += " "+self.url
        return '<%s:%-8s %s>' % ('clientserver', self.state, extra)
