# -*- coding: iso-8859-1 -*-
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
import wc.configuration
import wc.url
import wc.magic
import wc.filter
import wc.filter.rating
import wc.proxy
import wc.proxy.Server
import wc.proxy.auth
import wc.proxy.Headers
import wc.proxy.ServerPool


# DEBUGGING
PRINT_SERVER_HEADERS = 0
SPEEDCHECK_START = time.time()
SPEEDCHECK_BYTES = 0

FilterStages = [
    wc.filter.STAGE_RESPONSE_DECODE,
    wc.filter.STAGE_RESPONSE_MODIFY,
    wc.filter.STAGE_RESPONSE_ENCODE,
]

is_http_status = re.compile(r'^\d\d\d$').search
def get_response_data (response, url):
    """
    Parse a response status line into tokens (protocol, status, msg).
    """
    parts = response.split(None, 2)
    if len(parts) == 2:
        wc.log.warn(wc.LOG_PROXY, "Empty response message from %r", url)
        parts += ['Bummer']
    elif len(parts) != 3:
        wc.log.error(wc.LOG_PROXY, "Invalid response %r from %r",
                     response, url)
        parts = ['HTTP/1.0', "200", 'Ok']
    if not is_http_status(parts[1]):
        wc.log.error(wc.LOG_PROXY, "Invalid http statuscode %r from %r",
                     parts[1], url)
        parts[1] = "200"
    parts[1] = int(parts[1])
    return parts


def flush_decoders (decoders):
    """
    Flush given decoders and return flushed data.
    """
    data = ""
    while decoders:
        wc.log.debug(wc.LOG_PROXY, "flush decoder %s", decoders[0])
        data = decoders[0].flush()
        del decoders[0]
        for decoder in decoders:
            data = decoder.decode(data)
    return data


class HttpServer (wc.proxy.Server.Server):
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
        wc.log.debug(wc.LOG_PROXY, '%s reset', self)
        self.hostname = ''
        self.method = None
        self.document = ''
        self.response = ''
        self.headers = wc.proxy.Headers.WcMessage()
        # Handle each of these, left to right
        self.decoders = []
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
        wc.log.debug(wc.LOG_PROXY, "%s resetted", self)

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
            extra += self.document
        if hasattr(self, "client") and self.client:
            extra += " client"
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('server', self.state, extra)

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
        wc.log.debug(wc.LOG_PROXY, '%s write request\n%r', self, request)
        self.write(request)
        wc.log.debug(wc.LOG_PROXY, "%s write headers\n%s",
                     self, self.clientheaders)
        self.write("".join(self.clientheaders.headers))
        self.write('\r\n')
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
        if self.response.lower().startswith('http'):
            # Okay, we got a valid response line
            protocol, self.statuscode, tail = \
                                   get_response_data(self.response, self.url)
            # reconstruct cleaned response
            self.response = "%s %d %s" % (protocol, self.statuscode, tail)
            # Let the server pool know what version this is
            wc.proxy.ServerPool.serverpool.set_http_version(self.addr,
                                         wc.proxy.get_http_version(protocol))
        elif not self.response:
            # It's a blank line, so assume HTTP/0.9
            wc.log.warn(wc.LOG_PROXY, "%s got HTTP/0.9 response", self)
            wc.proxy.ServerPool.serverpool.set_http_version(self.addr, (0, 9))
            self.response = "%s 200 Ok" % self.protocol
            self.statuscode = 200
            self.recv_buffer = '\r\n' + self.recv_buffer
        else:
            # the HTTP line was missing, just assume that it was there
            # Example: http://ads.adcode.de/frame?11?3?10
            wc.log.warn(wc.LOG_PROXY,
                        _('invalid or missing response from %r: %r'),
                        self.url, self.response)
            wc.proxy.ServerPool.serverpool.set_http_version(self.addr, (1, 0))
            # put the read bytes back to the buffer
            self.recv_buffer = self.response + self.recv_buffer
            # look if the response line was a header
            # Example:
            # http://www.mail-archive.com/sqwebmail@inter7.com/msg03824.html
            if not wc.proxy.Headers.is_header(self.response):
                wc.log.warn(wc.LOG_PROXY,
                          _("missing headers in response from %r"), self.url)
                self.recv_buffer = '\r\n' + self.recv_buffer
            # fix the response
            self.response = "%s 200 Ok" % self.protocol
            self.statuscode = 200
        self.state = 'headers'
        stage = wc.filter.STAGE_RESPONSE
        self.attrs = wc.filter.get_filterattrs(self.url,
                                               self.client.localhost, [])
        self.response = wc.filter.applyfilter(stage, self.response,
                              "finish", self.attrs).strip()
        if self.statuscode >= 400:
            self.mime_types = None
        wc.log.debug(wc.LOG_PROXY, "%s response %r", self, self.response)

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
        msg = wc.proxy.Headers.WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        fp.close()
        # make a copy for later
        serverheaders = msg.copy()
        wc.log.debug(wc.LOG_PROXY, "%s server headers\n%s",
                     self, serverheaders)
        if self.statuscode == 100:
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        self.set_persistent(msg,
                     wc.proxy.ServerPool.serverpool.http_versions[self.addr])
        stage = wc.filter.STAGE_RESPONSE_HEADER
        self.attrs = wc.filter.get_filterattrs(self.url,
                        self.client.localhost, [stage],
                        clientheaders=self.client.headers,
                        serverheaders=serverheaders)
        try:
            self.headers = \
                wc.filter.applyfilter(stage, msg, "finish", self.attrs)
        except wc.filter.FilterRating, msg:
            wc.log.debug(wc.LOG_PROXY, "%s FilterRating from header: %s",
                         self, msg)
            if msg == wc.filter.rules.RatingRule.MISSING:
                # still have to look at content
                self.defer_data = True
            else:
                self._show_rating_deny(str(msg))
                return
        if self.statuscode in (301, 302):
            location = self.headers.get('Location')
            if location:
                host = wc.url.url_split(location)[1]
                if host in wc.proxy.dns_lookups.resolver.localhosts:
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
                                     serverheaders=serverheaders,
                                     headers=self.headers)
        # tell the MIME recognizer to ignore the type if
        # a) a MIME type is enforced
        # b) the MIME type is not supported
        mime = serverheaders.get('Content-Type')
        if self.mime_types or mime in wc.magic.unsupported_types:
            self.attrs['mimerecognizer_ignore'] = True
        wc.log.debug(wc.LOG_PROXY, "%s filtered headers %s",
                     self, self.headers)
        if self.defer_data:
            wc.log.debug(wc.LOG_PROXY, "deferring header data")
        else:
            self.client.server_response(self, self.response, self.statuscode,
                                        self.headers)
            # note: self.client could be None here

    def mangle_response_headers (self):
        """
        Modify response headers.
        """
        wc.proxy.Headers.server_set_headers(self.headers)
        self.bytes_remaining = wc.proxy.Headers.server_set_encoding_headers(
         self.headers, self.is_rewrite(), self.decoders, self.bytes_remaining)
        if self.bytes_remaining is None:
            self.persistent = False
        # 304 Not Modified does not send any type info, because it was cached
        if self.statuscode != 304:
            # copy decoders
            decoders = [d.__class__() for d in self.decoders]
            data = self.recv_buffer
            for decoder in decoders:
                data = decoder.decode(data)
            data += flush_decoders(decoders)
            wc.proxy.Headers.server_set_content_headers(
                                     self.headers, self.mime_types, self.url)

    def set_persistent (self, headers, http_ver):
        """
        Return True iff this server connection is persistent.
        """
        if http_ver >= (1,1):
            self.persistent = not wc.proxy.Headers.has_header_value(
                                              headers, 'Connection', 'Close')
        elif http_ver >= (1,0):
            self.persistent = wc.proxy.Headers.has_header_value(
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
        headers = wc.proxy.Headers.WcMessage()
        # XXX content type adaption?
        headers['Content-type'] = 'text/plain\r'
        headers['Location'] = 'http://%s:%d/rated.html?%s\r' % \
               (self.client.localhost, wc.configuration.config['port'], query)
        headers['Content-Length'] = '%d\r' % len(msg)
        wc.log.debug(wc.LOG_PROXY, "%s headers\n%s", self, headers)
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
        wc.log.debug(wc.LOG_PROXY, "%s process %d bytes", self, len(data))
        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)
            wc.log.debug(wc.LOG_PROXY, "%s %d bytes remaining",
                         self, self.bytes_remaining)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.decode(data)
            wc.log.debug(wc.LOG_PROXY, "%s have run decoder %s",
                         self, decoder)
            if not is_closed and decoder.closed:
                is_closed = True
        try:
            for stage in FilterStages:
               data = wc.filter.applyfilter(stage, data, "filter", self.attrs)
        except wc.filter.FilterWait, msg:
            wc.log.debug(wc.LOG_PROXY, "%s FilterWait %s", self, msg)
        except wc.filter.FilterRating, msg:
            wc.log.debug(wc.LOG_PROXY, "%s FilterRating from content %s",
                         self, msg)
            self._show_rating_deny(str(msg))
            return
        except wc.filter.FilterProxyError, e:
            self.client.error(e.status, e.msg, txt=e.text)
            self.handle_error("filter proxy error")
            return
        underflow = self.bytes_remaining is not None and \
                   self.bytes_remaining < 0
        if underflow:
            wc.log.warn(wc.LOG_PROXY,
                      _("server received %d bytes more than content-length"),
                      (-self.bytes_remaining))
        if self.statuscode != 407:
            if data:
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
            wc.log.debug(wc.LOG_PROXY,
                     "%s send %d bytes SSL tunneled data to client %s",
                     self, len(data), self.client)
            self.client.write(data)

    def process_recycle (self):
        """
        Recycle the server connection and put it in the server pool.
        """
        wc.log.debug(wc.LOG_PROXY, "%s recycling", self)
        if self.statuscode == 407 and wc.configuration.config['parentproxy']:
            wc.log.debug(wc.LOG_PROXY, "%s need parent proxy authentication",
                         self)
            if self.authtries:
                # we failed twice, abort
                self.authtries = 0
                self.handle_error('authentication error')
                wc.configuration.config['parentproxycreds'] = None
                return
            self.authtries += 1
            challenges = wc.proxy.auth.get_header_challenges(self.headers,
                              'Proxy-Authenticate')
            wc.proxy.Headers.remove_headers(self.headers,
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
                attrs['uri'] = wc.proxy.auth.get_auth_uri(self.document)
                # with https, this is CONNECT
                attrs['method'] = self.method
                attrs['requireExtraQuotes'] = \
           self.headers.get('Server', '').lower().startswith('microsoft-iis')
            creds = wc.proxy.auth.get_credentials(challenges, **attrs)
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
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.flush", self)
        if not self.statuscode:
            wc.log.warn(wc.LOG_PROXY, "%s flush without status", self)
        data = flush_decoders(self.decoders)
        try:
            for stage in FilterStages:
               data = wc.filter.applyfilter(stage, data, "finish", self.attrs)
        except wc.filter.FilterWait, msg:
            wc.log.debug(wc.LOG_PROXY, "%s FilterWait %s", self, msg)
            # the filter still needs some data
            # to save CPU time make connection unreadable for a while
            self.set_unreadable(0.5)
            return False
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
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.set_unreadable", self)
        oldstate, self.state = self.state, 'unreadable'
        wc.proxy.make_timer(secs, lambda: self.set_readable(oldstate))

    def set_readable (self, state):
        """
        Make the connection readable again and close.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.set_readable", self)
        # the client might already have closed
        if self.client:
            self.state = state
            self.handle_close()
        else:
            wc.log.debug(wc.LOG_PROXY, "%s client is gone", self)

    def close_reuse (self):
        """
        Reset connection data, but to not close() the socket. Put this
        connection in server pool.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.close_reuse", self)
        assert not self.client, "reuse with open client"
        super(HttpServer, self).close_reuse()
        self.state = 'client'
        self.reset()
        # be sure to unreserve _after_ reset because of callbacks
        wc.proxy.ServerPool.serverpool.unreserve_server(self.addr, self)

    def close_ready (self):
        """
        Return True if connection has all data sent and is ready for closing.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.close_ready", self)
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
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.close_close", self)
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
            wc.proxy.ServerPool.serverpool.unregister_server(self.addr, self)
        assert not self.connected

    def handle_error (self, what):
        """
        Tell the client that connection had an error, and close the
        connection.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.handle_error %r",
                     self, what)
        if self.client:
            client, self.client = self.client, None
            client.server_abort(what)
        super(HttpServer, self).handle_error(what)

    def handle_close (self):
        """
        Close the connection.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.handle_close", self)
        self.persistent = False
        super(HttpServer, self).handle_close()

    def reconnect (self):
        """
        Reconnect to server.
        """
        wc.log.debug(wc.LOG_PROXY, "%s HttpServer.reconnect", self)
        # we still must have the client connection
        if not self.client:
            wc.log.error(wc.LOG_PROXY, "%s lost client on reconnect", self)
            return
        from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
        # note: self.client still the matchmaker object
        client = self.client.client
        client.state = 'request'
        self.client = None
        ClientServerMatchmaker(client, client.request,
                               self.clientheaders, # with new auth
                               client.content, mime_types=self.mime_types)


def speedcheck_print_status ():
    """
    Print speed statistics for connections.
    """
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        wc.log.debug(wc.LOG_PROXY, 'speed: %4d b/s',
                     (SPEEDCHECK_BYTES/elapsed))
        pass
    SPEEDCHECK_START = time.time()
    SPEEDCHECK_BYTES = 0
    wc.proxy.make_timer(5, speedcheck_print_status)
    #if wc.proxy.ServerPool.serverpool.map:
    #    print 'server pool:'
    #    for addr,set in wc.proxy.ServerPool.serverpool.map.items():
    #        for server,status in set.items():
    #            print '  %15s:%-4d %10s %s' % (addr[0], addr[1],
    #                                          status[0], server.hostname)
