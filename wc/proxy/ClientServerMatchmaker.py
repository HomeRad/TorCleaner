import dns_lookups, socket, mimetypes, re, base64, sha
import wc.proxy
from wc.proxy import spliturl
from ServerPool import ServerPool
from ServerHandleDirectly import ServerHandleDirectly
from wc import i18n, config
from wc.debug import *
from wc.webgui import WebConfig

serverpool = ServerPool()

_localhosts = (
    'localhost',
    '127.0.0.1',
    '::1',
    'ip6-localhost',
    'ip6-loopback',
)

from HttpServer import HttpServer

class ClientServerMatchmaker:
    """
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
    def __init__ (self, client, request, headers, content, nofilter,compress):
        self.client = client
        self.request = request
        self.headers = headers
        self.compress = compress
        self.content = content
        self.nofilter = nofilter
        self.method, self.url, protocol = self.request.split()
        scheme, hostname, port, document = spliturl(self.url)
        if not document: document = '/'
        debug(HURT_ME_PLENTY, "Proxy: splitted url", scheme, hostname, port, document)
        if scheme=='file':
            # a blocked url is a local file:// link
            # this means we should _not_ use this proxy for local
            # file links :)
            mtype = mimetypes.guess_type(self.url)[0]
            config['requests']['valid'] += 1
            config['requests']['blocked'] += 1
            ServerHandleDirectly(self.client,
             'HTTP/1.0 200 OK\r\n',
             'Content-Type: %s\r\n\r\n'%(mtype or 'application/octet-stream'),
              open(document, 'rb').read())
            return

        if hostname in _localhosts and port==config['port']:
            return self.handle_local(document)
        if hostname.startswith('noproxy.'):
            hostname = hostname[8:]
            self.url = "%s://%s:%d%s" % (scheme, hostname, port, document)
        # prepare DNS lookup
        if config['parentproxy']:
            self.hostname = config['parentproxy']
            self.port = config['parentproxyport']
            self.document = self.url
            if config['parentproxyuser']:
                p = base64.decodestring(config['parentproxypass'])
                auth = "%s:%s" % (config['parentproxyuser'], p)
                auth = "Basic "+base64.encodestring(auth).strip()
                self.headers['Proxy-Authorization'] = auth
        else:
            self.hostname = hostname
            self.port = port
            self.document = document
        # append information for wcheaders tool
        wc.proxy.HEADERS.append((self.url, 'client', self.headers.headers))
        # start DNS lookup
        self.state = 'dns'
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_local (self, document):
        debug(HURT_ME_PLENTY, "Proxy: handle local request for", document)
        if self.client and self.client.addr[0] not in _localhosts:
            self.client.error(403, i18n._("Forbidden"),
                              wc.proxy.access_denied(self.client.addr))
        elif not WebConfig.handle_document(document, self.client):
            self.client.error(404, i18n._("Not found"),
              i18n._("Invalid path %s") % `document`)


    def handle_dns (self, hostname, answer):
        assert self.state == 'dns'

        if not self.client.connected:
            # The browser has already closed this connection, so abort
            return
        if answer.isFound():
            self.ipaddr = answer.data[0]
	    self.state = 'server'
            self.find_server()
        elif answer.isRedirect():
            # Let's use a different hostname
            new_url = answer.data
            if self.port != 80:
	        new_url += ':%s' % self.port
            new_url += self.document
            self.state = 'done'
            config['requests']['valid'] += 1
            ServerHandleDirectly(
              self.client,
              'HTTP/1.0 301 Use different host\r\n',
              'Content-type: text/html\r\n'
              'Location: http://%s\r\n'
              '\r\n' % new_url,
              i18n._('Host %s is an abbreviation for %s')%(hostname, answer.data))
        else:
            # Couldn't look up the host, so close this connection
            self.state = 'done'
            config['requests']['error'] += 1
            self.client.error(504, i18n._("Host not found"),
                i18n._('Host %s not found .. %s')%(hostname, answer.data))
            return

    def find_server (self):
        assert self.state == 'server'
        addr = (self.ipaddr, self.port)
        if not self.client.connected:
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # if http version is <1.1 and expect header found: 417
            if self.headers.get('Expect')=='100-continue' and \
               serverpool.http_versions.get(addr, 1.1) < 1.1:
                self.client.error(417, i18n._("Expectation failed"),
                           i18n._("Server does not understand HTTP/1.1"))
                return
            # Let's reuse it
            debug(BRING_IT_ON, 'Proxy: resurrecting', server)
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
        assert self.state == 'connect'
        if not self.client.connected:
            # The client has aborted, so let's return this server
            # connection to the pool
            server.reuse()
            return

        self.server = server
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
                                        self.url)


    def server_abort (self):
        # The server had an error, so we need to tell the client
        # that we couldn't connect
        if self.client.connected:
            self.client.error(503, i18n._("No response from server"))


    def server_close (self):
        debug(BRING_IT_ON, 'Proxy: resurrection failed', self.server.sequence_number, self.server)

        # Look for a server again
        if self.server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection.  Let's find another server object.
            self.state = 'server'
            self.find_server()
        else:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            if self.client.connected:
                self.client.error(503, i18n._("Server closed connection"))


    def server_response (self, response, headers):
        # Okay, transfer control over to the real client
        if self.client.connected:
            config['requests']['valid'] += 1
            self.server.client = self.client
            self.client.server_response(self.server, response, headers)
        else:
            self.server.client_abort()

