import rfc822, time, sys
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from ServerHandleDirectly import ServerHandleDirectly
from UnchunkStream import UnchunkStream
from wc import i18n, config, ip, remove_headers
from wc.proxy import log, match_host
from wc.proxy.auth import get_proxy_auth_challenge, check_proxy_auth
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


    def error (self, code, msg, txt='', auth=''):
        self.state = 'done'
        content = HTML_TEMPLATE % \
            {'title': 'Proxy Error %d %s' % (code, msg),
             'header': 'Bummer!',
             'content': 'Proxy Error %d %s<br>%s<br>' % \
                        (code, msg, txt),
            }
        if auth:
            auth = 'Proxy-Authenticate: %s\r\n'%auth
            http_ver = '1.1'
        else:
            http_ver = '1.0'
        ServerHandleDirectly(self,
            'HTTP/%s %d %s\r\n' % (http_ver, code, msg),
            'Server: Proxy\r\n' +\
            'Content-type: text/html\r\n' +\
            auth +\
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
            debug(BRING_IT_ON, "Client: request", self.request)
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
            # note: we do not enforce a maximum url length
            self.state = 'headers'


    def process_headers (self):
        i = self.recv_buffer.find('\r\n\r\n')
        if i >= 0: # Two newlines ends headers
            i += 4 # Skip over newline terminator
            # the first 2 chars are the newline of request
            fp = StringIO(self.read(i)[2:])
            msg = rfc822.Message(fp)
            # put unparsed data (if any) back to the buffer
            msg.rewindbody()
            self.recv_buffer = fp.read() + self.recv_buffer
            # work on these headers
            self.compress = client_set_proxy_headers(msg)
            # filter headers
            self.headers = applyfilter(FILTER_REQUEST_HEADER,
                              msg, fun="finish", attrs=self.nofilter)
            # add decoders
            self.decoders = []
            self.bytes_remaining = get_content_length(self.headers)
            # chunked encoded
            if self.headers.has_key('Transfer-Encoding'):
                # XXX don't look at value, assume chunked encoding for now
                debug(BRING_IT_ON, 'Client: Transfer-encoding:', `self.headers['transfer-encoding']`)
                self.decoders.append(UnchunkStream())
                client_remove_encoding_headers(self.headers)
                self.bytes_remaining = None
            debug(HURT_ME_PLENTY, "Client: Headers", `str(self.headers)`)
            if config["proxyuser"]:
                if not self.headers.has_key('Proxy-Authentication'):
                    return self.error(407,
                          i18n._("Proxy Authentication Required"),
                          auth=get_proxy_auth_challenge())
                auth = check_proxy_auth(self.headers['Proxy-Authentication'])
                if auth:
                    return self.error(407,
                          i18n._("Proxy Authentication Required"), auth=auth)
            if self.method in ['OPTIONS','TRACE'] and \
               get_max_forwards(self.headers)==0:
                # XXX display options ?
                self.state = 'done'
                return ServerHandleDirectly(self, 'HTTP/1.1 200 OK\r\n',
                                   'Content-Type: text/plain\r\n\r\n', '')
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
                    self.bytes_remaining < 0
        if underflow:
            print >>sys.stderr, "Warning: client received"+\
               " %d bytes more than content-length" % (-self.bytes_remaining)
        if is_closed or self.bytes_remaining==0:
            data = applyfilter(FILTER_REQUEST_DECODE, "",
    	                   fun="finish", attrs=self.nofilter)
            data = applyfilter(FILTER_REQUEST_DECODE, data,
    	                   fun="finish", attrs=self.nofilter)
            data = applyfilter(FILTER_REQUEST_DECODE, data,
    	                   fun="finish", attrs=self.nofilter)
            self.content += data
            if self.content and not self.headers.has_key('Content-Length'):
                self.headers['Content-Length'] = "%d\r"%len(self.content)
            # We're done reading content
            self.state = 'receive'
            # This object will call server_connected at some point
            ClientServerMatchmaker(self, self.request, self.headers,
                                   self.content, self.nofilter,
                                   self.compress)


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(NIGHTMARE, 'Client: server_response', self, `response`)
        self.write(response)
        self.write(''.join(headers.headers))
        self.write('\r\n')


    def server_content (self, data):
        assert self.server
        self.write(data)


    def server_close (self):
        assert self.server
        debug(NIGHTMARE, 'Client: server_close', self)
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None


    def server_abort (self):
        debug(NIGHTMARE, 'Client: server_abort', self)
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
        debug(HURT_ME_PLENTY, 'Client: handle_close', self)
        Connection.handle_close(self)
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.


    def close (self):
        debug(HURT_ME_PLENTY, 'Client: close', self)
        self.state = 'closed'
        Connection.close(self)


def get_content_length (headers):
    """get content length as int or 0 on error"""
    try:
        return int(headers.get('Content-Length', 0))
    except ValueError:
        print >>sys.stderr, "Invalid Content-Length value", headers.get('Content-Length')
    return 0


