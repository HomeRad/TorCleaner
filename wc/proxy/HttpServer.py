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
Connection handling proxy <--> http server.
"""

import time
import socket
import re
import urllib
import cStringIO as StringIO

import wc
import wc.log
import wc.strformat
import wc.configuration
import wc.url
import wc.magic
import wc.filter
import wc.http
import timer
import Server
import auth
import Headers
import ServerPool
import dns_lookups


# DEBUGGING
PRINT_SERVER_HEADERS = 0
SPEEDCHECK_START = time.time()
SPEEDCHECK_BYTES = 0

FilterStages = [
    wc.filter.STAGE_RESPONSE_DECODE,
    wc.filter.STAGE_RESPONSE_MODIFY,
    wc.filter.STAGE_RESPONSE_ENCODE,
]


class HttpServer (Server.Server):
    """
    HttpServer handles the connection between the proxy and a http server.
    It writes the client request to the server and sends answer data back
    to the client connection object, which is in most cases a HttpClient,
    but could also be a HttpProxyClient (for Javascript sources).
    """

    def __init__ (self, ipaddr, port, client):
        """
        Initialize connection data and connect to remove server.
        """
        super(HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.create_socket(self.get_family(ipaddr), socket.SOCK_STREAM)
        self.try_connect()

    def reset (self):
        """
        Reset connection values.
        """
        super(HttpServer, self).reset()
        assert None == wc.log.debug(wc.LOG_PROXY, '%s reset', self)
        self.hostname = ''
        self.method = None
        self.document = ''
        self.response = ''
        self.headers = wc.http.header.WcMessage()
        # for persistent connections
        self.persistent = False
        # initial filter attributes
        self.attrs = {'mime': None}
        # restrict number of authentication tries
        self.authtries = 0
        # numeric HTTP status code
        self.statuscode = None
        # number of content bytes remaining
        self.bytes_remaining = None
        # flag indicating to hold sending of data
        self.defer_data = False
        for f in ['MimeRecognizer', 'Compress']:
            # defer for all filters that change headers
            if f in wc.configuration.config['filters']:
                self.defer_data = True
        assert None == wc.log.debug(wc.LOG_PROXY, "%s resetted", self)

    def __repr__ (self):
        """
        Object description.
        """
        extra = ""
        if hasattr(self, "persistent") and self.persistent:
            extra += "persistent "
        hasaddr = hasattr(self, "addr") and self.addr
        hashostname = hasattr(self, "hostname") and self.hostname
        if hashostname:
            extra += self.hostname
        elif hasaddr:
            extra += self.addr[0]
        if hasaddr:
            extra += ":%d" % self.addr[1]
        if hasattr(self, "document"):
            extra += wc.strformat.limit(self.document, 200)
        if hasattr(self, "client") and self.client:
            extra += " client"
        if hasattr(self.socket, "state_string"):
            # SSL status string
            extra += " (%s)" % self.socket.state_string()
        return '<%s:%-8s %s>' % (self.__class__.__name__, self.state, extra)

    def process_connect (self):
        """
        Notify client that this server has connected.
        """
        assert self.state == 'connect'
        self.state = 'client'
        if self.client:
            self.client.server_connected(self)
        else:
            # Hm, the client no longer cares about us, so close
            self.close()

    def client_send_request (self, method, protocol, hostname, port, document,
                             headers, content, client, url, mime_types):
        """
        The client (matchmaker) sends the request to the server.
        """
        assert self.state == 'client', \
                                   "%s invalid state %r" % (self, self.state)
        self.method = method
        # the client protocol
        self.protocol = protocol
        self.client = client
        self.hostname = hostname
        self.port = port
        self.document = document
        self.content = content
        self.url = url
        # fix mime content-type for eg JavaScript
        self.mime_types = mime_types
        # remember client header for authorization resend
        self.clientheaders = headers
        if self.method != 'CONNECT':
            self.mangle_request_headers()
            self.send_request()

    def mangle_request_headers (self):
        """
        Modify request headers.
        """
        if wc.configuration.config['parentproxycreds']:
            # stored previous proxy authentication (for Basic and Digest auth)
            self.clientheaders['Proxy-Authorization'] = \
                          "%s\r" % wc.configuration.config['parentproxycreds']

    def send_request (self):
        """
        Send the request to the server, is also used to send a request
        twice for NTLM authentication.
        """
        assert self.method != 'CONNECT'
        request = '%s %s HTTP/1.1\r\n' % (self.method, self.document)
        assert None == wc.log.debug(wc.LOG_PROXY,
            '%s write request\n%r', self, request)
        self.write(request)
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s write headers\n%s", self, self.clientheaders)
        self.write("".join(self.clientheaders.headers))
        self.write('\r\n')
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s write content\n%r", self, self.content)
        self.write(self.content)
        self.state = 'response'

    def process_read (self):
        """
        Process read event by delegating it to process_* functions.
        """
        assert self.state != 'closed', \
                                  "%s invalid state %r" % (self, self.state)
        while True:
            if not self.client:
                # By the time this server object was ready to receive
                # data, the client has already closed the connection!
                # We never received the client_abort because the server
                # didn't exist back when the client aborted.
                self.client_abort()
                return
            if self.state == 'unreadable':
                return
            if self.delegate_read():
                break

    def process_response (self):
        """
        Look for response line and process it if found.
        """
        i = self.recv_buffer.find('\n')
        if i < 0:
            return
        self.response = self.read(i+1).strip()
        if self.response.lower().startswith('http/'):
            # Okay, we got a valid response line
            version, status, tail = \
                   wc.http.parse_http_response(self.response, self.url)
            # XXX reject invalid HTTP version
            # reconstruct cleaned response
            ver = "HTTP/%d.%d" % version
            self.response = "%s %d %s" % (ver, status, tail)
            self.statuscode = status
            # Let the server pool know what version this is
            ServerPool.serverpool.set_http_version(self.addr,
                                                            version)
        elif not self.response:
            # It's a blank line, so assume HTTP/0.9
            wc.log.warn(wc.LOG_PROXY, "%s got HTTP/0.9 response", self)
            ServerPool.serverpool.set_http_version(self.addr, (0, 9))
            self.response = "%s 200 OK" % self.protocol
            self.statuscode = 200
            self.recv_buffer = '\r\n' + self.recv_buffer
        else:
            # the HTTP line was missing, just assume that it was there
            # Example: http://ads.adcode.de/frame?11?3?10
            wc.log.warn(wc.LOG_PROXY,
                        'invalid or missing response from %r: %r',
                        self.url, self.response)
            ServerPool.serverpool.set_http_version(self.addr, (1, 0))
            # put the read bytes back to the buffer
            self.recv_buffer = self.response + self.recv_buffer
            # look if the response line was a header
            # Example:
            # http://www.mail-archive.com/sqwebmail@inter7.com/msg03824.html
            if not Headers.is_header(self.response):
                wc.log.warn(wc.LOG_PROXY,
                            "missing headers in response from %r", self.url)
                self.recv_buffer = '\r\n' + self.recv_buffer
            # fix the response
            self.response = "%s 200 OK" % self.protocol
            self.statuscode = 200
        self.state = 'headers'
        stage = wc.filter.STAGE_RESPONSE
        self.attrs = wc.filter.get_filterattrs(self.url,
                                               self.client.localhost, [])
        self.response = wc.filter.applyfilter(stage, self.response,
                              "finish", self.attrs).strip()
        if self.statuscode >= 400:
            self.mime_types = None
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s response %r", self, self.response)

    def process_headers (self):
        """
        Look for headers and process them if found.
        """
        # Headers are terminated by a blank line .. now in the regexp,
        # we want to say it's either a newline at the beginning of
        # the document, or it's a lot of headers followed by two newlines.
        # The cleaner alternative would be to read one line at a time
        # until we get to a blank line...
        m = re.match(r'^((?:[^\r\n]+\r?\n)*\r?\n)', self.recv_buffer)
        if not m:
            return
        # get headers
        fp = StringIO.StringIO(self.read(m.end()))
        msg = wc.http.header.WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        fp.close()
        # make a copy for later
        self.serverheaders = msg.copy()
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s server headers\n%s", self, self.serverheaders)
        if self.statuscode == 100:
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        self.set_persistent(msg,
                     ServerPool.serverpool.http_versions[self.addr])
        try:
            self.headers = self.filter_headers(msg)
        except wc.filter.FilterRating, err:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s FilterRating from header: %s", self, err)
            if err == wc.filter.rules.RatingRule.MISSING:
                # still have to look at content
                self.defer_data = True
            else:
                self._show_rating_deny(str(err))
                return
        if self.statuscode in (301, 302):
            location = self.headers.get('Location')
            if location:
                host = wc.url.url_split(location)[1]
                if host in dns_lookups.resolver.localhosts:
                    self.handle_error(_('redirection to localhost'))
                    return
        self.mangle_response_headers()
        if self.statuscode in (204, 304) or self.method == 'HEAD':
            # these response codes indicate no content
            self.state = 'recycle'
        else:
            self.state = 'content'
        self.attrs = wc.filter.get_filterattrs(self.url,
                                     self.client.localhost, FilterStages,
                                     clientheaders=self.client.headers,
                                     serverheaders=self.serverheaders,
                                     headers=self.headers)
        # tell the MIME recognizer to ignore the type if
        # a) a MIME type is enforced
        # b) the MIME type is not supported
        mime = self.serverheaders.get('Content-Type')
        if self.mime_types or mime in wc.magic.unsupported_types:
            self.attrs['mimerecognizer_ignore'] = True
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s filtered headers %s", self, self.headers)
        if self.defer_data:
            assert None == wc.log.debug(wc.LOG_PROXY, "deferring header data")
        else:
            self.client.server_response(self, self.response, self.statuscode,
                                        self.headers)
            # note: self.client could be None here

    def filter_headers (self, msg):
        stage = wc.filter.STAGE_RESPONSE_HEADER
        self.attrs = wc.filter.get_filterattrs(self.url,
                        self.client.localhost, [stage],
                        clientheaders=self.client.headers,
                        serverheaders=self.serverheaders)
        return wc.filter.applyfilter(stage, msg, "finish", self.attrs)

    def mangle_response_headers (self):
        """
        Modify response headers.
        """
        Headers.server_set_headers(self.headers, self.url)
        self.bytes_remaining = \
              Headers.server_set_encoding_headers(self)
        if self.bytes_remaining is None:
            self.persistent = False
        if self.statuscode == 304:
            # 304 Not Modified does not send any type info, because it
            # was cached
            return
        Headers.server_set_content_headers(
                    self.statuscode, self.headers, self.mime_types, self.url)

    def set_persistent (self, headers, http_ver):
        """
        Return True iff this server connection is persistent.
        """
        if http_ver >= (1, 1):
            self.persistent = not Headers.has_header_value(
                                              headers, 'Connection', 'Close')
        elif http_ver >= (1, 0):
            self.persistent = Headers.has_header_value(
                                         headers, 'Connection', 'Keep-Alive')
        else:
            self.persistent = False

    def is_rewrite (self):
        """
        Return True iff this server will modify content.
        """
        for ro in wc.configuration.config['mime_content_rewriting']:
            if ro.match(self.headers.get('Content-Type', '')):
                return True
        return False

    def _show_rating_deny (self, msg):
        """
        Requested page is rated.
        """
        query = urllib.urlencode({"url":self.url, "reason":msg})
        self.statuscode = 302
        response = "%s 302 %s" % (self.protocol, _("Moved Temporarily"))
        headers = wc.http.header.WcMessage()
        # XXX content type adaption?
        headers['Content-type'] = 'text/plain\r'
        headers['Location'] = 'http://%s:%d/rated.html?%s\r' % \
               (self.client.localhost, wc.configuration.config['port'], query)
        headers['Content-Length'] = '%d\r' % len(msg)
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s headers\n%s", self, headers)
        self.client.server_response(self, response, self.statuscode, headers)
        if not self.client:
            return
        self.client.server_content(msg)
        self.client.server_close(self)
        self.client = None
        self.state = 'recycle'
        self.defer_data = False
        self.persistent = False
        self.close()

    def process_content (self):
        """
        Process server data: filter it and write it to client.
        """
        data = self.read(self.bytes_remaining)
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s process %d bytes", self, len(data))
        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s %d bytes remaining", self, self.bytes_remaining)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.process(data)
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s have run decoder %s", self, decoder)
            if not is_closed and decoder.closed:
                is_closed = True
        try:
            for stage in FilterStages:
                data = wc.filter.applyfilter(stage, data, "filter", self.attrs)
        except wc.filter.FilterWait, msg:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s FilterWait %s", self, msg)
        except wc.filter.FilterRating, msg:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s FilterRating from content %s", self, msg)
            self._show_rating_deny(str(msg))
            return
        except wc.filter.FilterProxyError, e:
            self.handle_error("filter proxy error")
            return
        for encoder in self.encoders:
            data = encoder.process(data)
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s have run encoder %s", self, encoder)
        if self.bytes_remaining is not None and self.bytes_remaining < 0:
            # underflow
            wc.log.warn(wc.LOG_PROXY,
                      _("server received %d bytes more than content-length"),
                      (-self.bytes_remaining))
        if self.statuscode != 407 and data:
            if self.defer_data:
                # defer until data is non-empty, which ensures that
                # every filter above has seen at least some data
                self.defer_data = False
                self.client.server_response(self, self.response,
                                            self.statuscode, self.headers)
                if not self.client:
                    # client is gone
                    return
            self.client.server_content(data)
        if is_closed or self.bytes_remaining == 0:
            # either we ran out of bytes, or the decoder says we're done
            self.state = 'recycle'

    def process_client (self):
        """
        Gets called on SSL tunneled connections, delegates server data
        directly to the client without filtering.
        """
        if not self.client:
            # delay
            return
        data = self.read()
        if data:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s send %d bytes SSL tunneled data to client %s",
                self, len(data), self.client)
            self.client.write(data)

    def process_recycle (self):
        """
        Recycle the server connection and put it in the server pool.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, "%s recycling", self)
        if self.statuscode == 407 and wc.configuration.config['parentproxy']:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s need parent proxy authentication", self)
            if self.authtries:
                # we failed twice, abort
                self.authtries = 0
                self.handle_error('authentication error')
                wc.configuration.config['parentproxycreds'] = None
                return
            self.authtries += 1
            challenges = auth.get_header_challenges(self.headers,
                              'Proxy-Authenticate')
            Headers.remove_headers(self.headers,
                                                  ['Proxy-Authentication'])
            attrs = {
                'password_b64': wc.configuration.config['parentproxypass'],
                'username': wc.configuration.config['parentproxyuser'],
            }
            if 'NTLM' in challenges:
                attrs['type'] = challenges['NTLM'][0]['type']+1
                # must use GET for ntlm handshake
                if self.method != 'GET':
                    self.oldmethod = self.method
                    self.method = 'GET'
            if 'Digest' in challenges:
                # note: assume self.document is already url-encoded
                attrs['uri'] = auth.get_auth_uri(self.document)
                # with https, this is CONNECT
                attrs['method'] = self.method
                attrs['requireExtraQuotes'] = \
           self.headers.get('Server', '').lower().startswith('microsoft-iis')
            creds = auth.get_credentials(challenges, **attrs)
            # resubmit the request with proxy credentials
            self.state = 'client'
            wc.configuration.config['parentproxycreds'] = creds
            self.clientheaders['Proxy-Authorization'] = "%s\r" % creds
            self.send_request()
        else:
            # flush pending client data and try to reuse this connection
            self.delayed_close()

    def flush (self):
        """
        Flush data of decoders (if any) and filters and write it to
        the client. return True if flush was successful.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, "%s HttpServer.flush", self)
        if not self.statuscode and self.method != 'CONNECT':
            wc.log.warn(wc.LOG_PROXY, "%s flush without status", self)
            return True
        data = self.flush_coders(self.decoders)
        try:
            for stage in FilterStages:
                data = wc.filter.applyfilter(stage, data, "finish", self.attrs)
        except wc.filter.FilterWait, msg:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s FilterWait %s", self, msg)
            # the filter still needs some data
            # to save CPU time make connection unreadable for a while
            self.set_unreadable(1.0)
            return False
        except wc.filter.FilterRating, msg:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s FilterRating from content %s", self, msg)
            self._show_rating_deny(str(msg))
            return True
        data = self.flush_coders(self.encoders, data=data)
        # the client might already have closed
        if not self.client:
            return
        if self.defer_data:
            self.defer_data = False
            self.client.server_response(self, self.response,
                                        self.statuscode, self.headers)
            if not self.client:
                return
        if data and self.statuscode != 407:
            self.client.server_content(data)
        return True

    def set_unreadable (self, secs):
        """
        Make this connection unreadable for (secs) seconds.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.set_unreadable", self)
        oldstate, self.state = self.state, 'unreadable'
        timer.make_timer(secs, lambda: self.set_readable(oldstate))

    def set_readable (self, state):
        """
        Make the connection readable again and close.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.set_readable", self)
        # the client might already have closed
        if self.client:
            self.state = state
            self.handle_close()
        else:
            assert None == wc.log.debug(wc.LOG_PROXY,
                "%s client is gone", self)

    def close_reuse (self):
        """
        Reset connection data, but to not close() the socket. Put this
        connection in server pool.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.close_reuse", self)
        assert not self.client, "reuse with open client"
        super(HttpServer, self).close_reuse()
        self.state = 'client'
        self.reset()
        # be sure to unreserve _after_ reset because of callbacks
        ServerPool.serverpool.unreserve_server(self.addr, self)

    def close_ready (self):
        """
        Return True if connection has all data sent and is ready for closing.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.close_ready", self)
        if not (self.client and self.connected):
            # client has lost interest, or we closed already
            if self.client:
                self.client.server_close(self)
                self.client = None
            return True
        if not self.flush():
            return False
        if super(HttpServer, self).close_ready():
            if self.client:
                self.client.server_close(self)
                self.client = None
            return True
        return False

    def close_close (self):
        """
        Close the connection socket and remove this connection from
        the connection pool.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.close_close", self)
        # If a connect() failed, the handle_close has been called
        # directly. The client might still be open in this case.
        if self.client:
            self.client.server_close(self)
            self.client = None
        unregister = (self.connected and self.state != 'closed')
        if unregister:
            self.state = 'closed'
        super(HttpServer, self).close_close()
        if unregister:
            ServerPool.serverpool.unregister_server(self.addr, self)
        assert not self.connected

    def handle_error (self, what):
        """
        Tell the client that connection had an error, and close the
        connection.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.handle_error %r", self, what)
        if self.client:
            client, self.client = self.client, None
            client.server_abort(what)
        super(HttpServer, self).handle_error(what)

    def handle_close (self):
        """
        Close the connection.
        """
        assert None == wc.log.debug(wc.LOG_PROXY,
            "%s HttpServer.handle_close", self)
        self.persistent = False
        super(HttpServer, self).handle_close()


def speedcheck_print_status ():
    """
    Print speed statistics for connections.
    """
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        assert None == wc.log.debug(wc.LOG_PROXY,
            'speed: %4d b/s', (SPEEDCHECK_BYTES/elapsed))
        pass
    SPEEDCHECK_START = time.time()
    SPEEDCHECK_BYTES = 0
    timer.make_timer(5, speedcheck_print_status)
