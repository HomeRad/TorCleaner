# -*- coding: iso-8859-1 -*-
"""connection handling client <--> proxy"""
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, cgi, urlparse, os
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from ServerHandleDirectly import ServerHandleDirectly
from UnchunkStream import UnchunkStream
from wc import i18n, config
from wc.proxy import get_http_version, fix_http_version, url_norm, url_quote
from Headers import client_set_headers, client_get_max_forwards, WcMessage
from Headers import client_remove_encoding_headers, has_header_value
from wc.proxy.auth import *
from wc.proxy.auth.ntlm import NTLMSSP_NEGOTIATE
from wc.log import *
from wc.google import *
from wc.webgui import WebConfig
from wc.filter import FILTER_REQUEST
from wc.filter import FILTER_REQUEST_HEADER
from wc.filter import FILTER_REQUEST_DECODE
from wc.filter import FILTER_REQUEST_MODIFY
from wc.filter import FILTER_REQUEST_ENCODE
from wc.filter import applyfilter, get_filterattrs, FilterException

allowed_methods = ['GET', 'HEAD', 'CONNECT', 'POST']

class HttpClient (Connection):
    """States:
        request (read first line)
        headers (read HTTP headers)
        content (read HTTP POST content data)
        receive (read any additional data and forward it to the server)
        done    (done reading data, response already sent)
    """

    def __init__ (self, sock, addr):
        super(HttpClient, self).__init__(sock=sock)
        self.addr = addr
        self.state = 'request'
        self.server = None
        self.sequence_number = 1
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
        debug(PROXY, '%s error %s (%d)', str(self), `msg`, status)
        if status in google_try_status and config['try_google']:
            self.try_google(self.url, msg)
        else:
            err = i18n._('Proxy Error %d %s') % (status, msg)
            if txt:
                err = "%s (%s)" % (err, txt)
            form = None
            # this object will call server_connected at some point
            WebConfig(self, '/error.html', form, self.protocol, self.headers,
                  context={'error': err,}, status=status, msg=msg, auth=auth)


    def __repr__ (self):
        if self.request:
            try:
                extra = self.request.split()[1]
            except IndexError:
                extra = '???' + self.request
        else:
            extra = 'being read'
        return '<%s:%-8s persistent=%s %s>'%('client', self.state, self.persistent, extra)


    def process_read (self):
        # hmm, this occurs with WebCleaner as a parent of Oops Http Proxy
        assert not (self.state in ('receive','closed') and self.recv_buffer and self.method!='CONNECT'),\
         'client in state %s sent data %s'%(self.state, `self.recv_buffer`)

        while True:
            bytes_before = len(self.recv_buffer)
            state_before = self.state
            try:
                handler = getattr(self, 'process_'+self.state)
            except AttributeError:
                handler = lambda: None # NO-OP
            handler()
            bytes_after = len(self.recv_buffer)
            if (self.state=='done' or
                (bytes_before==bytes_after and state_before==self.state)):
                break


    def process_request (self):
        # One newline ends request
        i = self.recv_buffer.find('\r\n')
        if i < 0: return
        # self.read(i) is not including the newline
        self.request = self.read(i)
        info(ACCESS, '%s - %s - %s', self.addr[0],
             time.ctime(time.time()), self.request)
        try:
            self.method, self.url, protocol = self.request.split()
        except ValueError:
            self.error(400, i18n._("Can't parse request"))
            return
        if self.method not in allowed_methods:
            self.error(405, i18n._("Method Not Allowed"))
            return
        # fix broken url paths, and unquote
        self.url = url_norm(self.url)
        if not self.url:
            self.error(400, i18n._("Empty URL"))
            return
        self.attrs = get_filterattrs(self.url, [FILTER_REQUEST])
        self.protocol = fix_http_version(protocol)
        self.http_ver = get_http_version(self.protocol)
        self.request = "%s %s %s" % (self.method, url_quote(self.url), self.protocol)
        debug(PROXY, "%s request %s", str(self), `self.request`)
        self.request = applyfilter(FILTER_REQUEST, self.request,
                                   "finish", self.attrs)
        # refresh with filtered request data
        self.method, self.url, self.protocol = self.request.split()
        # enforce a maximum url length
        if len(self.url) > 1024:
            error(PROXY, "%s request url length %d chars is too long", str(self), len(self.url))
            self.error(400, i18n._("URL too long"))
            return
        if len(self.url) > 255:
            warn(PROXY, "%s request url length %d chars is very long", str(self), len(self.url))
        # and unquote again
        self.url = url_norm(self.url)
        self.state = 'headers'


    def process_headers (self):
        # Two newlines ends headers
        i = self.recv_buffer.find('\r\n\r\n')
        if i < 0: return
        i += 4 # Skip over newline terminator
        # the first 2 chars are the newline of request
        fp = StringIO(self.read(i)[2:])
        msg = WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        debug(PROXY, "%s client headers \n%s", str(self), str(msg))
        filters = [FILTER_REQUEST_HEADER,
                   FILTER_REQUEST_DECODE,
                   FILTER_REQUEST_MODIFY,
                   FILTER_REQUEST_ENCODE,
                  ]
        self.attrs = get_filterattrs(self.url, filters, headers=msg)
        # look if client wants persistent connections
        if self.http_ver >= (1,1):
            self.persistent = not has_header_value(msg, 'Proxy-Connection', 'Close') and \
                              not has_header_value(msg, 'Connection', 'Close')
        elif self.http_ver >= (1,0):
            self.persistent = has_header_value(msg, 'Proxy-Connection', 'Keep-Alive') or \
                              has_header_value(msg, 'Connection', 'Keep-Alive')
        else:
            self.persistent = False
        # work on these headers
        client_set_headers(msg)
        # filter headers
        self.headers = applyfilter(FILTER_REQUEST_HEADER,
                                   msg, "finish", self.attrs)
        # add decoders
        self.decoders = []
        self.bytes_remaining = get_content_length(self.headers)
        # chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            debug(PROXY, '%s Transfer-encoding %s', str(self), `self.headers['Transfer-encoding']`)
            self.decoders.append(UnchunkStream())
            client_remove_encoding_headers(self.headers)
            self.bytes_remaining = None
        if config["proxyuser"]:
            creds = get_header_credentials(self.headers, 'Proxy-Authorization')
            if not creds:
                auth = ", ".join(get_challenges())
                self.error(407, i18n._("Proxy Authentication Required"), auth=auth)
                return
            if 'NTLM' in creds:
                if creds['NTLM'][0]['type']==NTLMSSP_NEGOTIATE:
                    auth = ",".join(creds['NTLM'][0])
                    self.error(407, i18n._("Proxy Authentication Required"), auth=auth)
                    return
            # XXX the data=None argument should hold POST data
            if not check_credentials(creds, username=config['proxyuser'],
                                     password_b64=config['proxypass'],
                                     uri=get_auth_uri(self.url),
                                     method=self.method, data=None):
                warn(AUTH, "Bad proxy authentication from %s", self.addr[0])
                auth = ", ".join(get_challenges())
                self.error(407, i18n._("Proxy Authentication Required"), auth=auth)
                return
        if self.method in ['OPTIONS', 'TRACE'] and \
           client_get_max_forwards(self.headers)==0:
            # XXX display options ?
            self.state = 'done'
            ServerHandleDirectly(self, '%s 200 OK'%self.protocol, 200,
                      WcMessage(StringIO('Content-Type: text/plain\r\n\r\n')), '')
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
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        data = applyfilter(FILTER_REQUEST_DECODE, data, "filter", self.attrs)
        data = applyfilter(FILTER_REQUEST_MODIFY, data, "filter", self.attrs)
        data = applyfilter(FILTER_REQUEST_ENCODE, data, "filter", self.attrs)
        self.content += data
        underflow = self.bytes_remaining is not None and \
                    self.bytes_remaining < 0
        if underflow:
            warn(PROXY, "client received %d bytes more than content-length",
                 (-self.bytes_remaining))
        if is_closed or self.bytes_remaining==0:
            data = applyfilter(FILTER_REQUEST_DECODE, "", "finish", self.attrs)
            data = applyfilter(FILTER_REQUEST_MODIFY, data, "finish", self.attrs)
            data = applyfilter(FILTER_REQUEST_ENCODE, data, "finish", self.attrs)
            self.content += data
            if self.content and not self.headers.has_key('Content-Length'):
                self.headers['Content-Length'] = "%d\r"%len(self.content)
            # We're done reading content
            self.state = 'receive'
            self.server_request()


    def process_receive (self):
        """called for tunneled ssl connections
        XXX will also be called on pipelining?
        """
        if not self.server:
            # server is not yet there, delay
            return
        self.server.write(self.read())


    def server_request (self):
        assert self.state=='receive', "%s server_request in state receive" % str(self)
        # This object will call server_connected at some point
        ClientServerMatchmaker(self, self.request, self.headers,
                               self.content)


    def server_response (self, server, response, status, headers):
        # try google options
        assert server.connected, "%s server was not connected" % str(self)
        debug(PROXY, '%s server_response %s (%d)', str(self), `response`, status)
        if status in google_try_status and config['try_google']:
            server.client_abort()
            self.try_google(self.url, response)
        else:
            self.server = server
            self.write("%s\r\n"%response)
            if not headers.has_key('Content-Length'):
                # without content length the client can not determine
                # when all data is sent
                self.persistent = False
            # note: headers is a WcMessage object, not a dict
            self.write("".join(headers.headers))
            self.write('\r\n')


    def try_google (self, url, response):
        debug(PROXY, '%s try_google %s', str(self), `response`)
        context = get_google_context(url, response)
        form = None
        WebConfig(self, '/google.html', form, self.protocol, self.headers,
                  context=context)


    def server_content (self, data):
        assert self.server, "%s server_content had no server" % str(self)
        self.write(data)


    def server_close (self):
        assert self.server, "%s server_close had no server" % str(self)
        debug(PROXY, '%s server_close', str(self))
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None


    def server_abort (self):
        debug(PROXY, '%s server_abort', str(self))
        self.close()


    def handle_error (self, what):
        super(HttpClient, self).handle_error(what)
        # We should close the server connection
        if self.server:
            server, self.server = self.server, None
            server.client_abort()


    def handle_close (self):
        # The client closed the connection, so cancel the server connection
        debug(PROXY, '%s handle_close', str(self))
        self.send_buffer = ''
        super(HttpClient, self).handle_close()
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.


    def handle_local (self):
        assert self.state=='receive'
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            self.error(403, i18n._("Invalid Method"))
            return
        # get cgi form data
        form = self.get_form_data()
        debug(PROXY, '%s handle_local', str(self))
        # this object will call server_connected at some point
        WebConfig(self, self.url, form, self.protocol, self.headers)


    def get_form_data (self):
        form = None
        if self.method=='GET':
            # split off query string and parse it
            qs = urlparse.urlsplit(self.url)[3]
            if qs:
                form = cgi.parse_qs(qs)
        elif self.method=='POST':
            # XXX this uses FieldStorage internals
            form = cgi.FieldStorage(fp=StringIO(self.content),
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST'})
        return form


    def close (self):
        debug(PROXY, '%s close', str(self))
        self.state = 'closed'
        super(HttpClient, self).close()


    def reuse (self):
        debug(PROXY, '%s reuse', str(self))
        self.state = 'request'
        self.persistent = False


def get_content_length (headers):
    """get content length as int or 0 on error"""
    try:
        return int(headers.get('Content-Length', 0))
    except ValueError:
        warn(PROXY, "invalid Content-Length value %s", headers.get('Content-Length', ''))
    return 0

