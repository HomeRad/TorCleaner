import rfc822, time, sys
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from ServerHandleDirectly import ServerHandleDirectly
from UnchunkStream import UnchunkStream
from wc import i18n, config, ip, remove_headers
from wc.proxy import log, match_host
from wc.webgui.WebConfig import HTML_TEMPLATE
from wc.debug import *
from wc.filter import FILTER_REQUEST
from wc.filter import FILTER_REQUEST_HEADER
from wc.filter import FILTER_REQUEST_DECODE
from wc.filter import FILTER_REQUEST_MODIFY
from wc.filter import FILTER_REQUEST_ENCODE
from wc.filter import applyfilter

class HttpClient (Connection):
    """States:
        request (read first line)
        headers (read HTTP headers)
        data    (read any additional data and forward it to the server)
        done    (done reading data, response already sent)
    """

    def __init__ (self, socket, addr):
        Connection.__init__(self, socket)
        self.addr = addr
        self.state = 'request'
        self.server = None
        self.request = ''
        self.decoders = [] # Handle each of these, left to right
        self.headers = None
        self.bytes_remaining = None # for content only
        self.content = ''
        host = self.addr[0]
        hosts, nets, nil = config['allowedhosts']
        if not ip.host_in_set(host, hosts, nets):
            print >>sys.stderr, host, "access denied"
            self.close()


    def error (self, code, msg, txt=''):
        self.state = 'done'
        content = HTML_TEMPLATE % \
            {'title': 'Proxy Error %d %s' % (code, msg),
             'header': 'Bummer!',
             'content': 'Proxy Error %d %s<br>%s<br>' % \
                        (code, msg, txt),
            }
        if config['proxyuser']:
            auth = 'Proxy-Authenticate: Basic realm="unknown"\r\n'
            http_ver = '1.1'
        else:
            auth = ''
            http_ver = '1.0'
        ServerHandleDirectly(self,
            'HTTP/%s %d %s\r\n' % (http_ver, code, msg),
            'Server: Proxy\r\n' +\
            'Content-type: text/html\r\n' +\
            '%s'%auth +\
            '\r\n', content)


    def __repr__ (self):
        if self.state != 'request':
            try: extra = self.request.split()[1][7:] # Remove http://
            except: extra = '???' + self.request
            #if len(extra) > 46: extra = extra[:43] + '...'
        else:
            extra = 'being read'
        return '<%s:%-8s %s>' % ('client', self.state, extra)


    def process_read (self):
        # hmm, this occurs with WebCleaner as a parent of Oops Http Proxy
        assert not (self.state in ('receive','closed') and self.recv_buffer),\
         'client in state %s sent data %s'%(self.state, `self.recv_buffer`)

        while "True":
            bytes_before = len(self.recv_buffer)
            state_before = self.state
            try: handler = getattr(self, 'process_'+self.state)
            except AttributeError: handler = lambda:None # NO-OP
            handler()
            bytes_after = len(self.recv_buffer)
            if (self.state=='done' or
                (bytes_before==bytes_after and state_before==self.state)):
                break


    def process_request (self):
        i = self.recv_buffer.find('\r\n')
        if i >= 0: # One newline ends request
            # self.read(i) is not including the newline
            self.request = self.read(i)
            self.nofilter = {'nofilter': match_host(self.request)}
            debug(BRING_IT_ON, "Proxy: request", self.request)
            self.request = applyfilter(FILTER_REQUEST, self.request,
                           fun="finish", attrs=self.nofilter)
            log('%s - %s - %s\n' % (self.addr[0],
                time.ctime(time.time()), self.request))
            try: self.method, url, protocol = self.request.split()
            except:
                config['requests']['error'] += 1
                return self.error(400, i18n._("Can't parse request"))
            if not url:
                config['requests']['error'] += 1
                return self.error(400, i18n._("Empty URL"))
            self.state = 'headers'


    def process_headers (self):
        i = self.recv_buffer.find('\r\n\r\n')
        if i >= 0: # Two newlines ends headers
            i += 4 # Skip over newline terminator
            # the first 2 chars are the newline of request
            data = self.read(i)[2:]
            self.headers = rfc822.Message(StringIO(data))
            #debug(HURT_ME_PLENTY, "Proxy: C/Headers", `self.headers.headers`)
            # set via header
            via = self.headers.get('Via', "").strip()
            if via: via += " "
            via += "1.1 unknown\r"
            self.headers['Via'] = via
            self.headers = applyfilter(FILTER_REQUEST_HEADER,
                 self.headers, fun="finish", attrs=self.nofilter)
            # remember if client understands gzip
            self.compress = 'identity'
            encodings = self.headers.get('Accept-Encoding', '')
            for accept in encodings.split(','):
                if ';' in accept:
                    accept, q = accept.split(';', 1)
                if accept.strip().lower() in ('gzip', 'x-gzip'):
                    self.compress = 'gzip'
                    break
            # we understand gzip, deflate and identity
            self.headers['Accept-Encoding'] = \
                    'gzip;q=1.0, deflate;q=0.9, identity;q=0.5\r'
            # add decoders
            self.decoders = []
            self.bytes_remaining = int(self.headers.get('Content-Length', 0))
            # Chunked encoded
            if self.headers.get('Transfer-Encoding') is not None:
                debug(BRING_IT_ON, 'Proxy: C/Transfer-encoding:', `self.headers['transfer-encoding']`)
                self.decoders.append(UnchunkStream())
                # remove encoding header
                to_remove = ["Transfer-Encoding"]
                if self.headers.get("Content-Length") is not None:
                    print >>sys.stderr, 'Warning: chunked encoding should not have Content-Length'
                    to_remove.append("Content-Length")
                self.bytes_remaining = None
                remove_headers(self.headers, to_remove)
                # add warning
                self.headers['Warning'] = "214 Transformation applied\r"
            debug(HURT_ME_PLENTY, "Proxy: C/Headers", `str(self.headers)`)
            if config["proxyuser"] and not self.check_proxy_auth():
                return self.error(407, i18n._("Proxy Authentication Required"))
            if self.method=='OPTIONS':
                mf = int(self.headers.get('Max-Forwards', -1))
                if mf==0:
                    # XXX display options ?
                    self.state = 'done'
                    ServerHandleDirectly(self,
                       'HTTP/1.0 200 OK\r\n',
                       'Content-Type: text/plain\r\n\r\n',
                       '')
                    return
                if mf>0:
                    self.headers['Max-Forwards'] = mf-1
            self.state = 'content'


    def process_content (self):
        data = self.read(self.bytes_remaining)
        if self.bytes_remaining is not None:
            # Just pass everything through to the server
            # NOTE: It's possible to have 'chunked' encoding here,
            # and then the current system of counting bytes remaining
            # won't work; we have to deal with chunks
            self.bytes_remaining -= len(data)
        is_closed = 0
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        data = applyfilter(FILTER_REQUEST_DECODE, data,
                           attrs=self.nofilter)
        data = applyfilter(FILTER_REQUEST_MODIFY, data,
                           attrs=self.nofilter)
        data = applyfilter(FILTER_REQUEST_ENCODE, data,
                           attrs=self.nofilter)
        self.content += data
        underflow = self.bytes_remaining is not None and \
                    self.bytes_remaining <= 0
        if underflow:
            print >>sys.stderr, "Warning: client received %d bytes more than content-length" % (-self.bytes_remaining)
        if is_closed or underflow:
            data = applyfilter(FILTER_REQUEST_DECODE, "",
    	                   fun="finish", attrs=self.nofilter)
            data = applyfilter(FILTER_REQUEST_DECODE, data,
    	                   fun="finish", attrs=self.nofilter)
            data = applyfilter(FILTER_REQUEST_DECODE, data,
    	                   fun="finish", attrs=self.nofilter)
            self.content += data
            if not self.headers.has_key('Content-Length'):
                self.headers['Content-Length'] = str(len(self.content))
            # We're done reading content
            self.state = 'receive'
            # This object will call server_connected at some point
            ClientServerMatchmaker(self, self.request, self.headers,
                                   self.content, self.nofilter,
                                   self.compress)


    def check_proxy_auth (self):
        if self.headers.get("Proxy-Authorization") is None:
            return None
        auth = self.headers['Proxy-Authorization']
        if not auth.startswith("Basic "):
            return None
        auth = base64.decodestring(auth[6:])
        if ':' not in auth:
            return None
        _user,_pass = auth.split(":", 1)
        if _user!=config['proxyuser']:
            return None
        if config['proxypass'] and \
           _pass!=base64.decodestring(config['proxypass']):
            return None
        return "True"


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(NIGHTMARE, 'Proxy: C/Server response', self, `response`)
        self.write(response)
        self.write(''.join(headers.headers))
        self.write('\r\n')


    def server_content (self, data):
        assert self.server
        self.write(data)


    def server_close (self):
        assert self.server
        debug(NIGHTMARE, 'Proxy: C/Server close', self)
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None


    def server_abort (self):
        debug(NIGHTMARE, 'Proxy: C/Server abort', self)
        self.close()
        self.server = None


    def handle_error (self, what, type, value, tb=None):
        Connection.handle_error(self, what, type, value, tb=tb)
        # We should close the server connection
        if self.server:
            server, self.server = self.server, None
            server.client_abort()


    def handle_close (self):
        # The client closed the connection, so cancel the server connection
        self.send_buffer = ''
        debug(HURT_ME_PLENTY, 'Proxy: C/handle_close', self)
        Connection.handle_close(self)
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.


    def close (self):
        debug(HURT_ME_PLENTY, 'Proxy: C/close', self)
        self.state = 'closed'
        Connection.close(self)
