import dns_lookups, socket, mimetypes, re
import wc.proxy
from ServerPool import ServerPool
from ServerHandleDirectly import ServerHandleDirectly
from wc import _,debug,config
from wc.debug_levels import *

serverpool = ServerPool()

_localhosts = (
    'localhost',
    '127.0.0.1',
    '::1',
    'ip6-localhost',
    'ip6-loopback',
)
_intre = re.compile("^\d+$")

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
    def error(self, code, msg, txt=""):
        content = wc.proxy.HTML_TEMPLATE % \
            {'title': "WebCleaner Proxy Error %d %s" % (code, msg),
             'header': "Bummer!",
             'content': "WebCleaner Proxy Error %d %s<br>%s<br>" % \
                        (code, msg, txt),
            }
        ServerHandleDirectly(self.client,
            'HTTP/1.0 %d %s\r\n',
            'Server: WebCleaner Proxy\r\n'
            'Content-type: text/html\r\n'
            '\r\n', content)


    def __init__(self, client, request, headers, content, nofilter):
        self.client = client
        self.request = request
        self.headers = headers
        self.content = content
        self.nofilter = nofilter
        self.url = ""
        try: self.method, self.url, protocol = request.split()
        except:
            config['requests']['error'] += 1
            self.error(400, _("Can't parse request"))
            return
        if not self.url:
            config['requests']['error'] += 1
            self.error(400, _("Empty URL"))
            return
        scheme, hostname, port, document = wc.proxy.spliturl(self.url)
        #debug(HURT_ME_PLENTY, "splitted url", scheme, hostname, port, document)
        if scheme=='file':
            # a blocked url is a local file:// link
            # this means we should _not_ use this proxy for local
            # file links :)
            mtype = mimetypes.guess_type(self.url)[0]
            config['requests']['valid'] += 1
            config['requests']['blocked'] += 1
            ServerHandleDirectly(self.client,
	        'HTTP/1.0 200 OK\r\n',
                'Content-Type: %s\r\n\r\n' % (mtype or 'application/octet-stream'),
                open(document, 'rb').read())
            return

        if hostname.lower()=='localhost' and port==config['port']:
            return self.handle_local(document)
        # append information for wcheaders tool
        wc.proxy.HEADERS.append((self.url, 0, self.headers.headers))
        # prepare DNS lookup
        if config['parentproxy']:
            self.hostname = config['parentproxy']
            self.port = config['parentproxyport']
            self.document = self.url
        else:
            self.hostname = hostname
            self.port = port
            self.document = document
        self.state = 'dns'
        dns_lookups.background_lookup(self.hostname, self.handle_dns)


    def handle_local(self, document):
        if self.client and self.client.addr[0] not in _localhosts:
            contenttype = "text/html"
            content = wc.proxy.access_denied(self.client.addr)
        elif document.startswith("/headers/"):
            contenttype = "text/plain"
            content = wc.proxy.text_headers()
        elif document.startswith("/connections/"):
            contenttype = "text/plain"
            content = wc.proxy.text_connections()
        else:
            contenttype = "text/html"
            content = wc.proxy.html_portal()
        ServerHandleDirectly(self.client,
            'HTTP/1.0 200 OK\r\n',
            'Content-Type: %s\r\n\r\n'%contenttype,
            content)


    def handle_dns(self, hostname, answer):
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
                'Host %s is an abbreviation for %s\r\n'
                % (hostname, answer.data))
        else:
            # Couldn't look up the host, so close this connection
            self.state = 'done'
            config['requests']['error'] += 1
            self.error(504, "Host not found",
                'Host %s not found .. %s\r\n' % (hostname, answer.data))
            return

    def find_server(self):
        assert self.state == 'server'
        addr = (self.ipaddr, self.port)
        if not self.client.connected:
            # The browser has already closed this connection, so abort
            return
        server = serverpool.reserve_server(addr)
        if server:
            # Let's reuse it
            #debug(BRING_IT_ON, 'resurrecting', server)
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


    def server_connected(self, server):
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


    def server_abort(self):
        # The server had an error, so we need to tell the client
        # that we couldn't connect
        if self.client.connected:
            self.client.server_no_response()


    def server_close(self):
        #debug(BRING_IT_ON, 'resurrection failed', self.server.sequence_number, self.server)

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
                self.client.server_no_response()


    def server_response(self, response, headers):
        # Okay, transfer control over to the real client
        if self.client.connected:
            config['requests']['valid'] += 1
            self.server.client = self.client
            self.client.server_response(self.server, response, headers)
        else:
            self.server.client_abort()

