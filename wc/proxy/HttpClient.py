# -*- coding: iso-8859-1 -*-
"""connection handling client <--> proxy"""
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, cgi, mimetypes, urlparse
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from ServerHandleDirectly import ServerHandleDirectly
from UnchunkStream import UnchunkStream
from wc import i18n, config, ip
from wc.proxy import fix_http_version
from Headers import client_set_headers, client_get_max_forwards, WcMessage
from Headers import client_remove_encoding_headers
from wc.proxy.auth import *
from wc.log import *
from wc.webgui import WebConfig
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

    def __init__ (self, sock, addr):
        super(HttpClient, self).__init__(sock=sock)
        self.addr = addr
        self.state = 'request'
        self.server = None
        self.request = ''
        self.decoders = [] # Handle each of these, left to right
        self.headers = {}
        self.bytes_remaining = None # for content only
        self.content = ''
        self.protocol = 'HTTP/1.0'
        self.url = ''
        host = self.addr[0]
        if not config.allowed(host):
            warn(PROXY, "host %s access denied", host)
            self.close()


    def error (self, status, msg, txt='', auth=''):
        self.state = 'done'
        # this object will call server_connected at some point
        context = {
            'title': i18n._('Proxy Error %d %s') % (status, msg),
            'error': txt,
        }
        form = None
        WebConfig(self, '/error.html', form, self.protocol, self.headers,
                  context=context, status=status, msg=msg, auth=auth)


    def __repr__ (self):
        if self.state != 'request':
            try:
                extra = self.request.split()[1][7:] # Remove http://
            except IndexError:
                extra = '???' + self.request
            #if len(extra) > 46: extra = extra[:43] + '...'
        else:
            extra = 'being read'
        return '<%s:%-8s %s>' % ('client', self.state, extra)


    def process_read (self):
        # hmm, this occurs with WebCleaner as a parent of Oops Http Proxy
        assert not (self.state in ('receive','closed') and self.recv_buffer),\
         'client in state %s sent data %s'%(self.state, `self.recv_buffer`)

        while True:
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
            info(ACCESS, '%s - %s - %s', self.addr[0],
                 time.ctime(time.time()), self.request)
            try:
                self.method, self.url, protocol = self.request.split()
            except ValueError:
                config['requests']['error'] += 1
                self.error(400, i18n._("Can't parse request"))
                return
            self.nofilter = {'nofilter': config.nofilter(self.url)}
            debug(PROXY, "Client: request %s", self.request)
            self.url = applyfilter(FILTER_REQUEST, self.url,
                                   fun="finish", attrs=self.nofilter)
            self.protocol = fix_http_version(protocol)
            self.request = "%s %s %s" % (self.method, self.url, self.protocol)
            if not self.url:
                config['requests']['error'] += 1
                self.error(400, i18n._("Empty URL"))
                return
            # note: we do not enforce a maximum url length
            self.state = 'headers'


    def process_headers (self):
        i = self.recv_buffer.find('\r\n\r\n')
        if i >= 0: # Two newlines ends headers
            i += 4 # Skip over newline terminator
            # the first 2 chars are the newline of request
            fp = StringIO(self.read(i)[2:])
            msg = WcMessage(fp)
            # put unparsed data (if any) back to the buffer
            msg.rewindbody()
            self.recv_buffer = fp.read() + self.recv_buffer
            # work on these headers
            self.compress = client_set_headers(msg)
            # filter headers
            self.headers = applyfilter(FILTER_REQUEST_HEADER,
                              msg, fun="finish", attrs=self.nofilter)
            # add decoders
            self.decoders = []
            self.bytes_remaining = get_content_length(self.headers)
            # chunked encoded
            if self.headers.has_key('Transfer-Encoding'):
                # XXX don't look at value, assume chunked encoding for now
                debug(PROXY, 'Client: Transfer-encoding: %s', `self.headers['transfer-encoding']`)
                self.decoders.append(UnchunkStream())
                client_remove_encoding_headers(self.headers)
                self.bytes_remaining = None
            debug(PROXY, "Client: Headers %s", `str(self.headers)`)
            if config["proxyuser"]:
                creds = get_header_credentials(self.headers, 'Proxy-Authorization')
                if not creds:
                    self.error(407, i18n._("Proxy Authentication Required"),
                               auth=", ".join(get_challenges()))
                    return
                # XXX should wait until POST data arrives
                if not check_credentials(creds, username=config['proxyuser'],
                                         password_b64=config['proxypass'],
                                         uri=self.url, method=self.method,
                                         data=None):
                    warn(PROXY, "Bad proxy authentication from %s", self.addr[0])
                    self.error(407, i18n._("Proxy Authentication Required"),
                               auth=", ".join(get_challenges()))
                    return
            if self.method in ['OPTIONS', 'TRACE'] and \
               client_get_max_forwards(self.headers)==0:
                # XXX display options ?
                self.state = 'done'
                ServerHandleDirectly(self, '%s 200 OK\r\n'%self.protocol,
                                     'Content-Type: text/plain\r\n\r\n', '')
                return
            self.state = 'content'


    def process_content (self):
        data = self.read(self.bytes_remaining)
        if self.bytes_remaining is not None:
            # Just pass everything through to the server
            # NOTE: It's possible to have 'chunked' encoding here,
            # and then the current system of counting bytes remaining
            # won't work; we have to deal with chunks
            self.bytes_remaining -= len(data)
        is_closed = False
        debug(PROXY, "Proxy: client data %s", blocktext(`data`, 72))
        debug(PROXY, "decoders", self.decoders)
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        debug(PROXY, "Proxy: client data decoded %s", blocktext(`data`, 72))
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
            warn(PROXY, "client received %d bytes more than content-length",
                 (-self.bytes_remaining))
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
            self.server_request()


    def server_request (self):
        assert self.state == 'receive'
        # This object will call server_connected at some point
        ClientServerMatchmaker(self, self.request, self.headers,
                               self.content, self.nofilter,
                               self.compress)


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(PROXY, 'Client: server_response %s %s', str(self), `response`)
        self.write("%s\r\n"%response)
        if hasattr(headers, "headers"):
            # write original Message object headers to preserve
            # case sensitivity (!)
            self.write("".join(headers.headers))
        else:
            for key,val in headers.items():
                header = "%s: %s\r\n" % (key, val.rstrip())
                self.write(header)
        self.write('\r\n')


    def server_content (self, data):
        assert self.server
        self.write(data)


    def server_close (self):
        assert self.server
        debug(PROXY, 'Client: server_close %s', str(self))
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None


    def server_abort (self):
        debug(PROXY, 'Client: server_abort %s', str(self))
        self.close()
        self.server = None


    def handle_error (self, what):
        super(HttpClient, self).handle_error(what)
        # We should close the server connection
        if self.server:
            server, self.server = self.server, None
            server.client_abort()


    def handle_close (self):
        # The client closed the connection, so cancel the server connection
        self.send_buffer = ''
        debug(PROXY, 'Client: handle_close %s', str(self))
        super(HttpClient, self).handle_close()
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.


    def handle_local (self):
        assert self.state == 'receive'
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            self.error(403, i18n._("Invalid Method"))
            return
        # get cgi form data
        form = None
        if self.method=='GET':
            # split off query string and parse it
            qs = urlparse.urlsplit(self.url)[3]
            if qs:
                form = cgi.parse_qs(qs)
        elif self.method=='POST':
            # XXX this uses FieldStorage internals?
            form = cgi.FieldStorage(fp=StringIO(self.content),
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST'})
        # this object will call server_connected at some point
        WebConfig(self, self.url, form, self.protocol, self.headers)



    def close (self):
        debug(PROXY, 'Client: close %s', str(self))
        self.state = 'closed'
        super(HttpClient, self).close()


def get_content_length (headers):
    """get content length as int or 0 on error"""
    try:
        return int(headers.get('Content-Length', 0))
    except ValueError:
        warn(PROXY, "invalid Content-Length value %s", headers.get('Content-Length', ''))
    return 0

