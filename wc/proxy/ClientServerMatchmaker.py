# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from cStringIO import StringIO
import dns_lookups
from wc.proxy.Headers import WcMessage
from ServerPool import ServerPool
from ServerHandleDirectly import ServerHandleDirectly
from wc import i18n, config
from wc.log import *
from wc.proxy import document_quote

# connection pool for persistent server connections
serverpool = ServerPool()

from HttpServer import HttpServer

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
        self.method, self.url, protocol = self.request.split()
        # prepare DNS lookup
        if config['parentproxy']:
            self.hostname = config['parentproxy']
            self.port = config['parentproxyport']
            self.document = self.url
            if config['parentproxycreds']:
                auth = config['parentproxycreds']
                self.headers['Proxy-Authorization'] = "%s\r"%auth
        else:
            self.hostname = client.hostname
            self.port = client.port
            self.document = document_quote(client.document)
        # start DNS lookup
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_dns (self, hostname, answer):
        assert self.state == 'dns'
        debug(PROXY, "%s handle dns", self)
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
            new_url = self.scheme+"://"+answer.data
            if self.port != 80:
	        new_url += ':%d' % self.port
            new_url += self.document
            info(PROXY, "%s redirecting %r", self, new_url)
            self.state = 'done'
            # XXX find http version!
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
        debug(PROXY, "%s find server", self)
        addr = (self.ipaddr, self.port)
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
            # There are too many connections right now, so register us
            # as an interested party for getting a connection later
            serverpool.register_callback(addr, self.find_server)
        else:
            debug(PROXY, "%s new connect to server", self)
            # Let's make a new one
            self.state = 'connect'
            # HttpServer eventually call server_connected
            server = HttpServer(self.ipaddr, self.port, self)
            serverpool.register_server(addr, server)


    def server_connected (self, server):
        """the server has connected"""
        debug(PROXY, "%s server_connected", self)
        assert self.state=='connect'
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.reuse()
            return
        if self.method=='CONNECT':
            self.state = 'response'
            headers = WcMessage(StringIO(''))
            self.server_response(server, 'HTTP/1.1 200 OK', 200, headers)
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
        server.client_send_request(self.method,
                                   self.hostname,
                                   self.port,
                                   self.document,
                                   self.headers,
                                   self.content,
                                   self,
                                   self.url,
                                   self.mime)


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
