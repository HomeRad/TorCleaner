# -*- coding: iso-8859-1 -*-
# Copyright (c) 2000, Amit Patel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of Amit Patel nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Connection handling client <--> proxy.
"""

import time
import re
import cgi
import urlparse
import cStringIO as StringIO

import wc.log
import wc.strformat
import wc.configuration
import wc.http
import wc.url
import CodingConnection
import ClientServerMatchmaker
import ServerHandleDirectly
import decoder.UnchunkStream
import encoder.ChunkStream
import Allowed
import Headers
import auth
import dns_lookups
import HttpProxyClient
if wc.HasCrypto:
    from auth import ntlm
import wc.filter
import wc.webgui.webconfig
import wc.google

FilterStages = [
    wc.filter.STAGE_REQUEST_DECODE,
    wc.filter.STAGE_REQUEST_MODIFY,
    wc.filter.STAGE_REQUEST_ENCODE,
]

hostattr = re.compile(r"^(?i)([-a-z0-9\.]+)\.wc-([-a-z0-9]+)$")

class HttpClient (CodingConnection.CodingConnection):
    """
    States:
     - request (read first line)
     - headers (read HTTP headers)
     - content (read HTTP POST content data)
     - receive (read any additional data and forward it to the server)
     - done    (done reading data, response already sent)
     - closed  (this connection is closed)
    """

    def __init__ (self, sock, addr):
        """
        Initialize connection data, test if client connection is allowed.
        """
        super(HttpClient, self).__init__('request', sock=sock)
        self.addr = addr
        self.localhost = self.socket.getsockname()[0]
        assert None == wc.log.debug(wc.LOG_PROXY, "Connection to %s from %s",
                     self.socket.getsockname(), self.addr)
        self.allow = Allowed.AllowedHttpClient()
        host = self.addr[0]
        if not self.allow.host(host):
            wc.log.warn(wc.LOG_PROXY, "host %s access denied", host)
            self.close()

    def reset (self):
        """
        Reset connection state.
        """
        super(HttpClient, self).reset()
        assert None == wc.log.debug(wc.LOG_PROXY, '%s reset', self)
        self.state = 'request'
        self.server = None
        self.request = ''
        # remembers server headers
        self.headers = {}
        self.bytes_remaining = None # for content only
        self.content = ''
        self.compress = "identity" # acceptable compression for client
        self.version = (1, 1)
        self.method = ''
        self.url = ''
        self.needs_redirect = False

    def error (self, status, msg, txt='', auth_challenges=None):
        """
        Display error page.
        """
        self.state = 'done'
        assert None == wc.log.debug(wc.LOG_PROXY,
            '%s error %r (%d)', self, msg, status)
        if status in wc.google.google_try_status and \
           wc.configuration.config['try_google']:
            self.try_google(self.url, msg)
        else:
            err = _('Proxy Error %d %s') % (status, msg)
            if txt:
                err = "%s (%s)" % (err, txt)
            form = None
            # this object will call server_connected at some point
            protocol = "HTTP/%d.%d" % self.version
            wc.webgui.webconfig.WebConfig(self, '/error.html', form, protocol,
                      self.headers, localcontext={'error': err,},
                      status=status, msg=msg,
                      auth_challenges=auth_challenges).send()

    def __repr__ (self):
        """
        Object representation.
        """
        extra = ""
        if hasattr(self, "persistent") and self.persistent:
            extra += "persistent "
        if hasattr(self, "server") and self.server:
            extra += "server "
        if hasattr(self, "request") and self.request:
            try:
                request = self.request.split()[1]
            except IndexError:
                request = '???'+self.request
            extra += wc.strformat.limit(request, 200)
        else:
            extra += 'being read'
        if hasattr(self.socket, "state_string"):
            # SSL status string
            extra += " (%s)" % self.socket.state_string()
        return '<%s:%-8s %s>' % (self.__class__.__name__, self.state, extra)

    def process_read (self):
        """
        Delegate read according to current connection state.
        """
        assert self.state != 'closed'
        while True:
            if self.state == 'done':
                break
            if self.delegate_read():
                break

    def process_request (self):
        """
        Read request, split it up and filter it.
        """
        # One newline ends request
        i = self.recv_buffer.find('\r\n')
        if i < 0:
            return
        # self.read(i) is not including the newline
        # still strip() it from whitespace
        request = self.read(i).strip()
        method, url, version = wc.http.parse_http_request(request)
        # check request
        # sets self.method, self.url, self.version
        if not self.check_request(method, url, version):
            # error has been sent
            return
        # build request
        request = "%s %s HTTP/1.1" % (self.method, self.url)
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s request %r", self, request)
        # filter request
        stage = wc.filter.STAGE_REQUEST
        self.attrs = wc.filter.get_filterattrs(self.url,
                                               self.localhost, [stage])
        request = self.check_host_attrs(request)
        if self.attrs.get('show'):
            # return html doc showing active filters
            headers = wc.http.header.WcMessage()
            headers['Content-Type'] = 'text/html\r'
            headers['Server'] = 'WebCleaner\r'
            def callback (headers):
                mime = Headers.get_content_type(headers, self.url)
                body = wc.filter.show_rules(self.url, mime)
                ServerHandleDirectly.ServerHandleDirectly(self,
                 'HTTP/%d.%d 200 OK' % self.version, 200, headers, body)
            hpc = HttpProxyClient.HttpProxyClient(self.localhost,
                                                  self.url, method="HEAD")
            hpc.add_header_handler(callback)
            headers = Headers.get_wc_client_headers(hpc.hostname)
            ClientServerMatchmaker.ClientServerMatchmaker(
                 hpc, hpc.request, headers, '')
            self.state = 'done'
            return
        request = wc.filter.applyfilter(stage, request, "finish", self.attrs)
        self.request = request
        # final request checking
        if not self.fix_request():
            # error has been sent
            return
        wc.log.info(wc.LOG_ACCESS, '%s - %s - %s', self.addr[0],
                    time.ctime(time.time()), self.request)
        self.state = 'headers'

    def check_request (self, method, url, version):
        res = True
        if not self.allow.method(method):
            self.error(405, _("Method not allowed"))
            res = False
        self.method = method
        # fix broken url paths
        self.url = wc.url.url_norm(url)[0]
        if not self.url:
            self.error(400, _("Empty URL"))
            res = False
        if not ((0, 9) <= version <= (1, 1)):
            self.error(505, _("HTTP version not supported"))
            res = False
        self.version = version
        return res

    def fix_request (self):
        """
        Try to fix requests. Return False on error, else True.
        """
        # Refresh with filtered request data.
        # Assumes that the request now has correct syntax.
        self.method, self.url, protocol = self.request.split()
        # enforce a maximum url length
        if len(self.url) > Allowed.MAX_URL_LEN:
            wc.log.warn(wc.LOG_PROXY,
                         "%s request url length %d chars is too long",
                         self, len(self.url))
            self.error(414, _("URL too long"),
        txt=_('URL length limit is %d bytes.') % Allowed.MAX_URL_LEN)
            return False
        if len(self.url) > 1024:
            wc.log.warn(wc.LOG_PROXY,
                        "%s request url length %d chars is very long",
                        self, len(self.url))
        # unquote and norm url
        self.needs_redirect = "\\" in self.url
        self.url = wc.url.url_norm(self.url)[0]
        # fix CONNECT urls
        if self.method == 'CONNECT':
            # XXX scheme could also be nntps
            self.scheme = 'https'
            self.hostname, self.port = wc.url.splitport(self.url, port=443)
            self.document = '/'
        else:
            self.scheme, self.hostname, self.port, self.document = \
                                                wc.url.url_split(self.url)
            # Add missing trailing slash.
            if not self.document:
                self.document = '/'
        # Some clients (eg. SSL client) send partial URI's without scheme,
        # hostname and port to clients, so we have to handle this.
        if not self.scheme:
            self.scheme = self.get_default_scheme()
            self.port = wc.url.default_ports[self.scheme]
        if not self.allow.is_allowed(self.method, self.scheme, self.port):
            wc.log.warn(wc.LOG_PROXY, "Unallowed request %r", self.request)
            self.error(403, _("Forbidden"))
            return False
        # request is ok
        return True

    def get_default_scheme (self):
        """
        Get default URL scheme.
        """
        return "http"

    def check_host_attrs (self, request):
        """
        Check if host name defines some config attributes to honor.
        """
        parts = list(wc.url.url_split(self.url))
        attrmatch = hostattr.search(parts[1] or "")
        if attrmatch:
            parts[1] = self.hostname = attrmatch.group(1)
            self.url = wc.url.url_unsplit(parts)
            request = "%s %s HTTP/1.1" % (self.method, self.url)
            self.attrs[attrmatch.group(2)] = True
        return request

    def process_headers (self):
        """
        Read and filter client request headers.
        """
        # Two newlines ends headers
        i = self.recv_buffer.find('\r\n\r\n')
        if i < 0:
            return
        i += 4 # Skip over newline terminator
        # the first 2 chars are the newline of request
        fp = StringIO.StringIO(self.read(i)[2:])
        msg = wc.http.header.WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        fp.close()
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s client headers \n%s", self, msg)
        self.fix_request_headers(msg)
        self.clientheaders = msg.copy()
        self.set_persistent(msg, self.version)
        self.mangle_request_headers(msg)
        self.compress = Headers.client_set_encoding_headers(msg)
        self.headers = self.filter_headers(msg)
        # if content-length header is missing, assume zero length
        self.bytes_remaining = \
               Headers.get_content_length(self.headers, 0)
        # chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            assert None == wc.log.debug(wc.LOG_PROXY,
                '%s Transfer-encoding %r',
                self, self.headers['Transfer-encoding'])
            unchunker = decoder.UnchunkStream.UnchunkStream(self)
            self.decoders.append(unchunker)
            chunker = encoder.ChunkStream.ChunkStream(self)
            self.encoders.append(chunker)
            self.bytes_remaining = None
        if self.bytes_remaining is None:
            self.persistent = False
        if not self.headers.has_key('Host'):
            if self.version == (1, 1):
                wc.log.error(wc.LOG_PROXY, "%s missing Host: header", self)
                self.error(400, _("Bad Request"))
                return
        elif not self.hostname:
            host = self.headers['Host']
            self.hostname, self.port = wc.url.splitport(host, port=self.port)
            self.url = "%s://%s:%d%s" % (self.scheme, self.hostname, self.port, self.url)
            self.request = "%s %s HTTP/1.1" % (self.method, self.url)
            # XXX should filter request again
        if not self.hostname:
            wc.log.error(wc.LOG_PROXY, "%s missing hostname in request", self)
            self.error(400, _("Bad Request"))
            return
        # local request?
        if self.hostname in dns_lookups.resolver.localhosts and \
           self.port == wc.configuration.config['port']:
            # this is a direct proxy call, jump directly to content
            self.state = 'content'
            return
        # add missing host headers for HTTP/1.0
        if not self.headers.has_key('Host'):
            wc.log.warn(wc.LOG_PROXY,
                 "%s HTTP/1.0 request without Host header encountered", self)
        if self.port != wc.url.default_ports[self.get_default_scheme()]:
            self.headers['Host'] = "%s:%d\r" % (self.hostname, self.port)
        else:
            self.headers['Host'] = "%s\r" % self.hostname
        if wc.configuration.config["proxyuser"]:
            creds = auth.get_header_credentials(self.headers,
                       'Proxy-Authorization')
            if not creds:
                self.error(407, _("Proxy Authentication Required"),
                           auth_challenges=auth.get_challenges())
                return
            if 'NTLM' in creds:
                if creds['NTLM'][0]['type'] == \
                                       ntlm.NTLMSSP_NEGOTIATE:
                    attrs = {
                        'host': creds['NTLM'][0]['host'],
                        'domain': creds['NTLM'][0]['domain'],
                        'type': ntlm.NTLMSSP_CHALLENGE,
                    }
                    self.error(407, _("Proxy Authentication Required"),
                        auth_challenges=auth.get_challenges(**attrs))
                    return
            # XXX the data=None argument should hold POST data
            if not auth.check_credentials(creds,
                           username=wc.configuration.config['proxyuser'],
                           password_b64=wc.configuration.config['proxypass'],
                           uri=auth.get_auth_uri(self.url),
                           method=self.method, data=None):
                wc.log.warn(wc.LOG_AUTH, "Bad proxy authentication from %s",
                            self.addr[0])
                self.error(407, _("Proxy Authentication Required"),
                           auth_challenges=auth.get_challenges())
                return
        if self.method in ['OPTIONS', 'TRACE'] and \
           Headers.client_get_max_forwards(self.headers) == 0:
            # XXX display options ?
            self.state = 'done'
            headers = wc.http.header.WcMessage()
            headers['Content-Type'] = 'text/plain\r'
            ServerHandleDirectly.ServerHandleDirectly(self,
                 'HTTP/%d.%d 200 OK' % self.version, 200, headers, '')
            return
        if self.needs_redirect:
            self.state = 'done'
            headers = wc.http.header.WcMessage()
            headers['Content-Type'] = 'text/plain\r'
            headers['Location'] = '%s\r' % self.url
            ServerHandleDirectly.ServerHandleDirectly(self,
                'HTTP/%d.%d 302 Found' % self.version, 302, headers, '')
            return
        self.state = 'content'

    def filter_headers (self, msg):
        """
        Filter and return client headers.
        """
        stage = wc.filter.STAGE_REQUEST_HEADER
        self.attrs = wc.filter.get_filterattrs(self.url,
                       self.localhost, [stage],
                       clientheaders=self.clientheaders,
                       headers=msg)
        return wc.filter.applyfilter(stage, msg, "finish", self.attrs)

    def set_persistent (self, headers, http_ver):
        """
        Return True if connection is persistent.
        """
        # look if client wants persistent connections
        if http_ver >= (1, 1):
            self.persistent = \
              not (Headers.has_header_value(headers,
                     'Proxy-Connection', 'Close') or
                   Headers.has_header_value(headers,
                     'Connection', 'Close'))
        else:
            self.persistent = Headers.has_header_value(headers,
                                           "Proxy-Connection", "Keep-Alive")

    def fix_request_headers (self, headers):
        if headers.has_key('Host'):
            i = headers['Host'].find("\\")
            if i != -1:
                self.needs_redirect = True
                headers['Host'] = "%s\r" % headers['Host'][:i]

    def mangle_request_headers (self, headers):
        """
        Modify request headers.
        """
        Headers.client_set_headers(headers, self.url)

    def process_content (self):
        """
        Read and filter client request content.
        """
        data = self.read(self.bytes_remaining)
        if self.bytes_remaining is not None:
            # Just pass everything through to the server
            # NOTE: It's possible to have 'chunked' encoding here,
            # and then the current system of counting bytes remaining
            # won't work; we have to deal with chunks
            self.bytes_remaining -= len(data)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.process(data)
            if not is_closed:
                is_closed = decoder.closed
        for stage in FilterStages:
            data = wc.filter.applyfilter(stage, data, "filter", self.attrs)
        for encoder in self.encoders:
            data = encoder.process(data)
        self.content += data
        underflow = self.bytes_remaining is not None and \
                    self.bytes_remaining < 0
        if underflow:
            wc.log.warn(wc.LOG_PROXY,
                        "client received %d bytes more than content-length",
                        -self.bytes_remaining)
        if is_closed or self.bytes_remaining <= 0:
            data = self.flush_coders(self.decoders)
            for stage in FilterStages:
                data = wc.filter.applyfilter(stage, data, "finish",
                                             self.attrs)
            data = self.flush_coders(self.encoders, data=data)
            self.content += data
            if self.content:
                if self.method in ['GET', 'HEAD']:
                    wc.log.warn(wc.LOG_PROXY,
                                "Unexpected content in %s request: %r",
                                self.method, self.content)
                    if self.headers.has_key('Content-Length'):
                        del self.headers['Content-Length']
                elif not self.headers.has_key('Content-Length') and \
                     not self.headers.has_key('Transfer-Encoding'):
                    self.headers['Content-Length'] = \
                               "%d\r" % len(self.content)
            # We're done reading content
            self.state = 'receive'
            is_local = self.hostname in \
                       dns_lookups.resolver.localhosts and \
                       self.port in (wc.configuration.config['port'],
                                     wc.configuration.config['sslport'])
            if is_local:
                is_public_doc = self.allow.public_document(self.document)
            if wc.configuration.config['adminuser'] and \
               not wc.configuration.config['adminpass']:
                is_admin_doc = self.allow.admin_document(self.document)
                if is_local and (is_public_doc or is_admin_doc):
                    self.handle_local(is_public_doc=is_public_doc,
                                      is_admin_doc=is_admin_doc)
                else:
                    # ignore request, must init admin password
                    self.headers['Location'] = \
                      "http://%s:%d/adminpass.html\r" % \
               (self.socket.getsockname()[0], wc.configuration.config['port'])
                    self.error(302, _("Moved Temporarily"))
            elif is_local:
                # this is a direct proxy call
                self.handle_local(is_public_doc=is_public_doc)
            else:
                self.server_request()

    def process_receive (self):
        """
        Called for tunneled ssl connections.
        """
        if not self.server:
            # server is not yet there, delay
            return
        if self.method == "CONNECT":
            data = self.read()
            if data:
                assert None == wc.log.debug(wc.LOG_PROXY,
                        "%s send %d bytes SSL tunneled data to server %s",
                         self, len(data), self.server)
                self.server.write(data)
        else:
            wc.log.warn(wc.LOG_PROXY, "%s invalid data", self)

    def server_request (self):
        """
        Issue server request through ClientServerMatchmaker object.
        """
        assert self.state == 'receive', \
                             "%s server_request in non-receive state" % self
        assert None == wc.log.debug(wc.LOG_PROXY, "%s server_request", self)
        # this object will call server_connected at some point
        ClientServerMatchmaker.ClientServerMatchmaker(self,
                              self.request, self.clientheaders, self.content)

    def server_response (self, server, response, status, headers):
        """
        Read and filter server response data.
        """
        assert server.connected, "%s server was not connected" % self
        assert None == wc.log.debug(wc.LOG_PROXY,
            '%s server_response %r (%r)', self, response, status)
        # try google options
        if status in wc.google.google_try_status and \
           wc.configuration.config['try_google']:
            server.client_abort()
            self.try_google(self.url, response)
        else:
            self.server = server
            self.write("%s\r\n" % response)
            if not headers.has_key('Content-Length'):
                # without content length the client can not determine
                # when all data is sent
                self.persistent = False
            #self.set_persistent(headers, self.version)
            # note: headers is a WcMessage object, not a dict
            self.write("".join(headers.headers))
            self.write('\r\n')

    def try_google (self, url, response):
        """
        Display page with google cache links for requests page.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            '%s try_google %r', self, response)
        form = None
        protocol = "HTTP/%d.%d" % self.version
        wc.webgui.webconfig.WebConfig(self, '/google.html', form, protocol,
              self.headers,
              localcontext=wc.google.get_google_context(url, response)).send()

    def server_content (self, data):
        """
        The server received some content. Write it to the client.
        """
        assert self.server, "%s server_content(%r) had no server" % \
                            (self, data)
        if data:
            self.write(data)

    def server_close (self, server):
        """
        The server closed.
        """
        assert self.server, "%s server_close had no server" % self
        assert None == wc.log.debug(wc.LOG_PROXY, '%s server_close', self)
        if self.connected:
            self.delayed_close()
        else:
            self.close()
        self.server = None

    def server_abort (self, reason=""):
        """
        The server aborted the connection.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s server_abort', self)
        self.close()

    def handle_error (self, what):
        """
        An error occured, close the connection and inform the server.
        """
        # close the server connection
        if self.server:
            self.server.client_abort()
            self.server = None
        super(HttpClient, self).handle_error(what)

    def handle_close (self):
        """
        The client closed the connection, so cancel the server connection.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s handle_close', self)
        self.send_buffer = ''
        if self.server:
            self.server.client_abort()
            self.server = None
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.
        super(HttpClient, self).handle_close()

    def handle_local (self, is_public_doc=False, is_admin_doc=False):
        """
        Handle local request by delegating it to the web configuration.
        """
        assert self.state == 'receive'
        assert None == wc.log.debug(wc.LOG_PROXY, '%s handle_local', self)
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            self.error(403, _("Invalid Method"))
            return
        # check admin pass
        if not (is_public_doc or is_admin_doc) and \
           wc.configuration.config["adminuser"]:
            creds = auth.get_header_credentials(self.headers,
                                                         'Authorization')
            if not creds:
                self.error(401, _("Authentication Required"),
                           auth_challenges=auth.get_challenges())
                return
            if 'NTLM' in creds and creds['NTLM'][0]['type'] == \
               ntlm.NTLMSSP_NEGOTIATE:
                self.error(401, _("Authentication Required"),
                           auth_challenges=[",".join(creds['NTLM'][0])])
                return
            # XXX the data=None argument should hold POST data
            if not auth.check_credentials(creds,
                            username=wc.configuration.config['adminuser'],
                            password_b64=wc.configuration.config['adminpass'],
                            uri=auth.get_auth_uri(self.url),
                            method=self.method, data=None):
                wc.log.warn(wc.LOG_AUTH, "Bad authentication from %s",
                            self.addr[0])
                self.error(401, _("Authentication Required"),
                           auth_challenges=auth.get_challenges())
                return
        # get cgi form data
        form = self.get_form_data()
        # this object will call server_connected at some point
        protocol = "HTTP/%d.%d" % self.version
        wc.webgui.webconfig.WebConfig(self, self.url, form, protocol,
                                      self.headers).send()

    def get_form_data (self):
        """
        Return CGI form data from stored request.
        """
        form = None
        if self.method == 'GET':
            # split off query string and parse it
            qs = urlparse.urlsplit(self.url)[3]
            if qs:
                form = cgi.parse_qs(qs)
        elif self.method == 'POST':
            # XXX this uses FieldStorage internals
            form = cgi.FieldStorage(fp=StringIO.StringIO(self.content),
                                    headers=self.headers,
                                    environ={'REQUEST_METHOD': 'POST'})
        return form

    def close_reuse (self):
        """
        Reset connection state, leave connection alive for pipelining.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s close_reuse', self)
        super(HttpClient, self).close_reuse()
        self.reset()

    def close_close (self):
        """
        Close this connection.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s close_close', self)
        self.state = 'closed'
        super(HttpClient, self).close_close()
