import dns_lookups, socket, mimetypes, re, base64, sha
import wc.proxy
from wc.proxy import spliturl, fix_http_version
from ServerPool import ServerPool
from ServerHandleDirectly import ServerHandleDirectly
from wc import i18n, config
from wc.log import *
from wc.webgui import WebConfig

serverpool = ServerPool()

# XXX is this list of localhost stuff complete?
addrinfo = socket.gethostbyaddr(socket.gethostname())
_localhosts = {
    'localhost' : None,
    'loopback' : None,
    '127.0.0.1' : None,
    '::1' : None,
    'ip6-localhost' : None,
    'ip6-loopback' : None,
}
_localhosts[addrinfo[0]] = None
for h in addrinfo[1]:
    _localhosts[h] = None
for h in addrinfo[2]:
    _localhosts[h] = None

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
    def __init__ (self, client, request, headers, content, nofilter,
                  compress, mime=None):
        self.client = client
        self.request = request
        self.headers = headers
        self.compress = compress
        self.content = content
        self.nofilter = nofilter
        self.mime = mime
        debug(PROXY, "ClientServer: %s", `self.request`)
        self.method, self.url, protocol = self.request.split()
        # strip leading zeros and other stuff
        protocol = fix_http_version(protocol)
        scheme, hostname, port, document = spliturl(self.url)
        # some clients send partial URI's without scheme, hostname
        # and port to clients, so we have to handle this
        if not scheme:
            warn(PROXY, "partial request uri: %s", self.request)
            # default scheme is http
            scheme = "http"
        if scheme!='file' and not hostname:
            # the 'Host' header has to be there
            hostname = self.headers.get('Host')
            if not hostname:
                # we cannot handle the request
                self.client.error(400, i18n._("Incomplete Proxy Request"))
                return
        if scheme!='file' and not port:
            port = 80
        # fix missing trailing /
        if not document: document = '/'
        # fix missing host headers for HTTP/1.1
        if protocol=='HTTP/1.1' and not self.headers.has_key('Host'):
            self.headers['Host'] = hostname
            if port!=80:
                self.headers['Host'] += ":%d"%port
        debug(PROXY, "ClientServer: splitted url %s %s %d %s", scheme, hostname, port, document)
        if scheme=='file':
            # a blocked url is a local file:// link
            # this means we should _not_ use this proxy for local
            # file links :)
            mtype = mimetypes.guess_type(self.url)[0]
            config['requests']['valid'] += 1
            config['requests']['blocked'] += 1
            ServerHandleDirectly(self.client,
             'HTTP/1.1 200 OK\r\n',
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
        wc.proxy.HEADERS.append((self.url, 'client', self.headers.items()))
        # start DNS lookup
        self.state = 'dns'
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_local (self, document):
        debug(PROXY, "ClientServer: handle local request for %s", document)
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
	        new_url += ':%d' % self.port
            new_url += self.document
            self.state = 'done'
            config['requests']['valid'] += 1
            # XXX find http version!
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
            # Let's reuse it
            debug(PROXY, 'ClientServer: resurrecting %s', str(server))
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
        debug(PROXY, 'ClientServer: resurrection failed %d %s', self.server.sequence_number, str(self.server))
        # Look for a server again
        if self.server.sequence_number > 0:
            # It has already handled a request, so the server is allowed
            # to kill the connection.  Let's find another server object.
            self.state = 'server'
            self.find_server()
        elif self.client.connected:
            # The server didn't handle the original request, so we just
            # tell the client, sorry.
            self.client.error(503, i18n._("Server closed connection"))


    def server_response (self, response, headers):
        # Okay, transfer control over to the real client
        if self.client.connected:
            config['requests']['valid'] += 1
            self.server.client = self.client
            self.client.server_response(self.server, response, headers)
        else:
            self.server.client_abort()

