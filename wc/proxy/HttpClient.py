# -*- coding: iso-8859-1 -*-
"""connection handling client <--> proxy"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, cgi, urlparse, urllib, os
from cStringIO import StringIO
from StatefulConnection import StatefulConnection
from ClientServerMatchmaker import ClientServerMatchmaker
from ServerHandleDirectly import ServerHandleDirectly
from UnchunkStream import UnchunkStream
from wc import i18n, config
from wc.proxy import get_http_version, fix_http_version
from wc.url import spliturl, splitnport, url_norm, url_quote
from Headers import client_set_headers, client_get_max_forwards, WcMessage
from Headers import client_remove_encoding_headers, has_header_value
from Headers import get_content_length, client_set_encoding_headers
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
from wc.filter import applyfilter, get_filterattrs, FilterRating
from Allowed import AllowedHttpClient


_all_methods = ['GET', 'HEAD', 'CONNECT', 'POST', 'PUT']
def is_http_method (s):
    if len(s)<7:
        # not enough data, say yes for now
        return True
    for m in _all_methods:
        if s.startswith(m):
            return True
    return False


class HttpClient (StatefulConnection):
    """States:
        request (read first line)
        headers (read HTTP headers)
        content (read HTTP POST content data)
        receive (read any additional data and forward it to the server)
        done    (done reading data, response already sent)
        closed  (this connection is closed)
    """

    def __init__ (self, sock, addr):
        super(HttpClient, self).__init__('request', sock=sock)
        self.addr = addr
        self.allow = AllowedHttpClient()
        self.reset()
        host = self.addr[0]
        if not self.allow.host(host):
            warn(PROXY, "host %s access denied", host)
            self.close()


    def reset (self):
        self.state = 'request'
        self.server = None
        self.request = ''
        self.decoders = [] # Handle each of these, left to right
        self.headers = {} # remembers server headers
        self.bytes_remaining = None # for content only
        self.content = ''
        self.compress = "identity" # acceptable compression for client
        self.protocol = 'HTTP/1.0'
        self.url = ''


    def error (self, status, msg, txt='', auth=''):
        self.state = 'done'
        debug(PROXY, '%s error %r (%d)', self, msg, status)
        if status in google_try_status and config['try_google']:
            self.try_google(self.url, msg)
        else:
            err = i18n._('Proxy Error %d %s') % (status, msg)
            if txt:
                err = "%s (%s)" % (err, txt)
            form = None
            # this object will call server_connected at some point
            WebConfig(self, '/error.html', form, self.protocol, self.headers,
                      localcontext={'error': err,}, status=status, msg=msg,
                      auth=auth)


    def __repr__ (self):
        extra = self.persistent and "persistent " or ""
        if self.request:
            try:
                extra += self.request.split()[1]
            except IndexError:
                extra += '???'+self.request
        else:
            extra += 'being read'
        return '<%s:%-8s %s>'%('client', self.state, extra)


    def process_read (self):
        assert self.state!='closed'
        while True:
            if self.state=='done':
                break
            if self.delegate_read():
                break


    def process_request (self):
        # One newline ends request
        i = self.recv_buffer.find('\r\n')
        if i < 0:
            return
        # self.read(i) is not including the newline
        self.request = self.read(i)
        # basic request checking (more will be done below)
        try:
            self.method, self.url, protocol = self.request.split()
        except ValueError:
            self.error(400, i18n._("Can't parse request"))
            return
        if  not self.allow.method(self.method):
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
        debug(PROXY, "%s request %r", self, self.request)
        # filter request
        self.request = applyfilter(FILTER_REQUEST, self.request,
                                   "finish", self.attrs)
        # final request checking
        if not self.fix_request():
            return
        info(ACCESS, '%s - %s - %s', self.addr[0],
             time.ctime(time.time()), self.request)
        self.state = 'headers'


    def fix_request (self):
        # refresh with filtered request data
        self.method, self.url, self.protocol = self.request.split()
        # enforce a maximum url length
        if len(self.url) > 1024:
            error(PROXY, "%s request url length %d chars is too long", self, len(self.url))
            self.error(400, i18n._("URL too long"))
            return False
        if len(self.url) > 255:
            warn(PROXY, "%s request url length %d chars is very long", self, len(self.url))
        # and unquote again
        self.url = url_norm(self.url)
        # fix CONNECT urls
        if self.method=='CONNECT':
            # XXX scheme could also be nntps
            self.scheme = 'https'
            self.hostname, self.port = splitnport(self.url, 443)
            self.document = '/'
        else:
            self.scheme, self.hostname, self.port, self.document = spliturl(self.url)
            # fix missing trailing /
            if not self.document:
                self.document = '/'
        # some clients send partial URI's without scheme, hostname
        # and port to clients, so we have to handle this
        if not self.scheme:
            # default scheme is http
            self.scheme = 'http'
        if not self.allow.scheme(self.scheme):
            warn(PROXY, "%s forbidden scheme %r encountered", self, self.scheme)
            self.error(403, i18n._("Forbidden"))
            return False
        # check CONNECT values sanity
        if self.method == 'CONNECT':
            if self.scheme != 'https':
                warn(PROXY, "%s CONNECT method with forbidden scheme %r encountered", self, self.scheme)
                self.error(403, i18n._("Forbidden"))
                return False
            if not self.allow.connect_port(self.port):
                warn(PROXY, "%s CONNECT method with invalid port %r encountered", self, str(self.port))
                self.error(403, i18n._("Forbidden"))
                return False
        # request is ok
        return True


    def process_headers (self):
        # Two newlines ends headers
        i = self.recv_buffer.find('\r\n\r\n')
        if i < 0:
            return
        i += 4 # Skip over newline terminator
        # the first 2 chars are the newline of request
        fp = StringIO(self.read(i)[2:])
        msg = WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        fp.close()
        debug(PROXY, "%s client headers \n%s", self, msg)
        filters = [FILTER_REQUEST_HEADER,
                   FILTER_REQUEST_DECODE,
                   FILTER_REQUEST_MODIFY,
                   FILTER_REQUEST_ENCODE,
                  ]
        self.attrs = get_filterattrs(self.url, filters, headers=msg)
        self.persistent = self.get_persistent(msg, self.http_ver)
        self.mangle_request_headers(msg)
        self.compress = client_set_encoding_headers(msg)
        # filter headers
        self.headers = applyfilter(FILTER_REQUEST_HEADER,
                                   msg, "finish", self.attrs)
        # add decoders
        self.decoders = []
        self.bytes_remaining = get_content_length(self.headers)
        # chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            debug(PROXY, '%s Transfer-encoding %r', self, self.headers['Transfer-encoding'])
            self.decoders.append(UnchunkStream())
            client_remove_encoding_headers(self.headers)
            self.bytes_remaining = None
        if self.bytes_remaining is None:
            self.persistent = False
        if self.method=='CONNECT':
            if not self.headers.has_key('Host'):
                warn(PROXY, "%s CONNECT method without Host header encountered", self)
                self.error(403, i18n._("Forbidden"))
                return
        elif not self.hostname and self.headers.has_key('Host'):
            host = self.headers['Host']
            self.hostname, self.port = splitnport(host, 80)
        if not self.hostname:
            error(PROXY, "%s missing hostname in request", self)
            self.error(400, i18n._("Bad Request"))
        # local request?
        if self.hostname in config['localhosts'] and self.port==config['port']:
            # this is a direct proxy call, jump directly to content
            self.state = 'content'
            return
        # add missing host headers for HTTP/1.1
        if not self.headers.has_key('Host'):
            warn(PROXY, "%s request without Host header encountered", self)
            if port!=80:
                self.headers['Host'] = "%s:%d\r"%(self.hostname, self.port)
            else:
                self.headers['Host'] = "%s\r"%self.hostname
        if config["proxyuser"]:
            creds = get_header_credentials(self.headers, 'Proxy-Authorization')
            if not creds:
                auth = ", ".join(get_challenges())
                self.error(407, i18n._("Proxy Authentication Required"),
                           auth=auth)
                return
            if 'NTLM' in creds:
                if creds['NTLM'][0]['type']==NTLMSSP_NEGOTIATE:
                    auth = ",".join(creds['NTLM'][0])
                    self.error(407, i18n._("Proxy Authentication Required"),
                               auth=auth)
                    return
            # XXX the data=None argument should hold POST data
            if not check_credentials(creds, username=config['proxyuser'],
                                     password_b64=config['proxypass'],
                                     uri=get_auth_uri(self.url),
                                     method=self.method, data=None):
                warn(AUTH, "Bad proxy authentication from %s", self.addr[0])
                auth = ", ".join(get_challenges())
                self.error(407, i18n._("Proxy Authentication Required"),
                           auth=auth)
                return
        if self.method in ['OPTIONS', 'TRACE'] and \
           client_get_max_forwards(self.headers)==0:
            # XXX display options ?
            self.state = 'done'
            ServerHandleDirectly(self, '%s 200 OK'%self.protocol, 200,
                 WcMessage(StringIO('Content-Type: text/plain\r\n\r\n')), '')
            return
        self.state = 'content'


    def get_persistent (self, headers, http_ver):
        # look if client wants persistent connections
        if http_ver >= (1,1):
            persistent = not has_header_value(headers, 'Proxy-Connection', 'Close') and \
                         not has_header_value(headers, 'Connection', 'Close')
        else:
            # note: never do persistent connections for HTTP/1.0 clients
            persistent = False
        return persistent


    def mangle_request_headers (self, headers):
        client_set_headers(headers)


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
        if is_closed or self.bytes_remaining <= 0:
            data = applyfilter(FILTER_REQUEST_DECODE, "", "finish", self.attrs)
            data = applyfilter(FILTER_REQUEST_MODIFY, data, "finish", self.attrs)
            data = applyfilter(FILTER_REQUEST_ENCODE, data, "finish", self.attrs)
            self.content += data
            if self.content and not self.headers.has_key('Content-Length'):
                self.headers['Content-Length'] = "%d\r"%len(self.content)
            # We're done reading content
            self.state = 'receive'
            is_local = self.hostname in config['localhosts'] and \
               self.port in (config['port'], config['sslport'])
            if config['adminuser'] and not config['adminpass']:
                if is_local and self.allow.public_document(self.document):
                    self.handle_local(is_public_doc=True)
                else:
                    # ignore request, must init admin password
                    self.headers['Location'] = "http://localhost:%d/adminpass.html\r"%config['port']
                    self.error(302, i18n._("Moved Temporarily"))
            elif is_local:
                # this is a direct proxy call
                self.handle_local()
            else:
                self.server_request()


    def process_receive (self):
        """called for tunneled ssl connections
        """
        if not self.server:
            # server is not yet there, delay
            return
        if self.method=="CONNECT":
            self.server.write(self.read())
        #elif not self.persistent:
        #    warn(PROXY, "%s data in non-persistent receive state", self)
        # all other received data will be handled when the ongoing request
        # is finished


    def server_request (self):
        assert self.state=='receive', "%s server_request in non-receive state"%self
        # this object will call server_connected at some point
        ClientServerMatchmaker(self, self.request, self.headers,
                               self.content)


    def server_response (self, server, response, status, headers):
        assert server.connected, "%s server was not connected"%self
        debug(PROXY, '%s server_response %r (%d)', self, response, status)
        # try google options
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
        debug(PROXY, '%s try_google %r', self, response)
        form = None
        WebConfig(self, '/google.html', form, self.protocol, self.headers,
                  localcontext=get_google_context(url, response))


    def server_content (self, data):
        assert self.server, "%s server_content had no server"%self
        if data:
            self.write(data)


    def server_close (self, server):
        assert self.server, "%s server_close had no server"%self
        debug(PROXY, '%s server_close', self)
        if self.connected:
            self.delayed_close()
        else:
            self.close()
        self.server = None


    def server_abort (self):
        debug(PROXY, '%s server_abort', self)
        self.close()


    def handle_error (self, what):
        super(HttpClient, self).handle_error(what)
        # We should close the server connection
        if self.server:
            server, self.server = self.server, None
            server.client_abort()


    def handle_close (self):
        # The client closed the connection, so cancel the server connection
        debug(PROXY, '%s handle_close', self)
        self.send_buffer = ''
        super(HttpClient, self).handle_close()
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.


    def handle_local (self, is_public_doc=False):
        assert self.state=='receive'
        debug(PROXY, '%s handle_local', self)
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            self.error(403, i18n._("Invalid Method"))
            return
        # check admin pass
        if not is_public_doc and config["adminuser"]:
            creds = get_header_credentials(self.headers, 'Authorization')
            if not creds:
                auth = ", ".join(get_challenges())
                self.error(401, i18n._("Authentication Required"), auth=auth)
                return
            if 'NTLM' in creds:
                if creds['NTLM'][0]['type']==NTLMSSP_NEGOTIATE:
                    auth = ",".join(creds['NTLM'][0])
                    self.error(401, i18n._("Authentication Required"), auth=auth)
                    return
            # XXX the data=None argument should hold POST data
            if not check_credentials(creds, username=config['adminuser'],
                                     password_b64=config['adminpass'],
                                     uri=get_auth_uri(self.url),
                                     method=self.method, data=None):
                warn(AUTH, "Bad authentication from %s", self.addr[0])
                auth = ", ".join(get_challenges())
                self.error(401, i18n._("Authentication Required"), auth=auth)
                return
        # get cgi form data
        form = self.get_form_data()
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


    def close_reuse (self):
        debug(PROXY, '%s reuse', self)
        super(HttpClient, self).close_reuse()
        self.reset()


    def close_close (self):
        debug(PROXY, '%s close', self)
        self.state = 'closed'
        super(HttpClient, self).close_close()

