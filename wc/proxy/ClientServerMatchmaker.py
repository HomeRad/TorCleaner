# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from cStringIO import StringIO
import dns_lookups
import wc.proxy
from wc.proxy import spliturl, splitnport, fix_http_version
from wc.proxy.Headers import WcMessage
from ServerPool import ServerPool
from ServerHandleDirectly import ServerHandleDirectly
from wc import i18n, config
from wc.log import *

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
    def __init__ (self, client, request, headers, content, nofilter,
                  compress, mime=None):
        self.client = client
        self.server = None
        self.request = request
        self.headers = headers
        self.compress = compress
        self.content = content
        self.nofilter = nofilter
        self.mime = mime
        self.state = 'dns'
        self.method, self.url, protocol = self.request.split()
        # strip leading zeros and other stuff
        self.protocol = fix_http_version(protocol)
        self.scheme, hostname, port, document = spliturl(self.url)
        # some clients send partial URI's without scheme, hostname
        # and port to clients, so we have to handle this
        if not self.scheme:
            # default scheme is http
            self.scheme = "http"
        elif self.scheme != 'http':
            warn(PROXY, "Forbidden scheme encountered at %s", str(self))
            client.error(403, i18n._("Forbidden"))
            return
        if not hostname and self.headers.has_key('Host'):
            host = self.headers['Host']
            hostname, port = splitnport(host, 80)
        if not hostname or \
           (hostname in config['localhosts'] and port==config['port']):
            # this is a direct proxy call, delegate it to local handler
            client.handle_local()
            return
        # fix missing trailing /
        if not document:
            document = '/'
        # add missing host headers for HTTP/1.1
        if self.protocol=='HTTP/1.1' and not self.headers.has_key('Host'):
            if port!=80:
                self.headers['Host'] = "%s:%d\r"%(hostname, port)
            else:
                self.headers['Host'] = "%s\r"%hostname
        # prepare DNS lookup
        if config['parentproxy']:
            self.hostname = config['parentproxy']
            self.port = config['parentproxyport']
            self.document = self.url
            if config['parentproxycreds']:
                auth = config['parentproxycreds']
                self.headers['Proxy-Authorization'] = "%s\r"%auth
        else:
            self.hostname = hostname
            self.port = port
            self.document = document
        # append information for wcheaders tool
        wc.proxy.HEADERS.append((self.url, 'client', self.headers.items()))
        # start DNS lookup
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_dns (self, hostname, answer):
        assert self.state == 'dns'
        debug(PROXY, "%s handle dns", str(self))
        if not self.client.connected:
            warn(PROXY, "%s client closed after DNS", str(self))
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
            info(PROXY, "%s redirecting %s", str(self), `new_url`)
            self.state = 'done'
            config['requests']['valid'] += 1
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
            config['requests']['error'] += 1
            self.client.error(504, i18n._("Host not found"),
                i18n._('Host %s not found .. %s')%(hostname, answer.data))


    def find_server (self):
        """search for a connected server or make a new one"""
        assert self.state == 'server'
        debug(PROXY, "%s find server", str(self))
        addr = (self.ipaddr, self.port)
        if not self.client.connected:
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # Let's reuse it
            debug(PROXY, '%s resurrecting %s', str(self), str(server))
            self.state = 'connect'
            self.server_connected(server)
        elif serverpool.count_servers(addr)>=serverpool.connection_limit(addr):
            # There are too many connections right now, so register us
            # as an interested party for getting a connection later
            serverpool.register_callback(addr, self.find_server)
        else:
            # Let's make a new one
            self.state = 'connect'
            server = HttpServer(self.ipaddr, self.port, self)
            serverpool.register_server(addr, server)


    def server_connected (self, server):
        """the server has connected"""
        assert self.state == 'connect'
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.reuse()
            return
        self.server = server
        addr = (self.ipaddr, self.port)
        # check expectations
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
                       i18n._("Unsupported expectation `%s'")%expect)
            return
        # ok, assign server object
        self.state = 'response'
        # At this point, we tell the server that we are the client.
        # Once we get a response, we transfer to the real client.
        self.server.client_send_request(self.method,
                                        self.hostname, 
                                        self.document,
                                        self.headers,
                                        self.content,
                                        self,
					self.nofilter,
                                        self.url,
                                        self.mime)


    def server_abort (self):
        # The server had an error, so we need to tell the client
        # that we couldn't connect
        if self.client.connected:
            self.client.error(503, i18n._("No response from server"))


    def server_close (self):
        """the server has closed"""
        debug(PROXY, '%s resurrection failed %d %s', str(self), self.server.sequence_number, str(self.server))
        # Look for a server again
        if self.server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection. Let's find another server object.
            self.state = 'server'
            self.find_server()
        elif self.client.connected:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            self.client.error(503, i18n._("Server closed connection"))


    def server_response (self, response, status, headers):
        """the server got a response"""
        # Okay, transfer control over to the real client
        if self.client.connected:
            config['requests']['valid'] += 1
            self.server.client = self.client
            self.client.server_response(self.server, response, status, headers)
        else:
            self.server.client_abort()


    def __repr__ (self):
        if self.client:
            extra = "client"
        else:
            extra = ""
        extra += " "+self.url
        return '<%s:%-8s %s>' % ('clientserver', self.state, extra)
