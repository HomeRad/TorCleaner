# -*- coding: iso-8859-1 -*-
"""connection handling proxy <--> http server"""
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, socket, re, urlparse

from cStringIO import StringIO
from Server import Server
from wc.proxy import make_timer, get_http_version, create_inet_socket
from wc.proxy.auth import *
from Headers import server_set_headers, server_set_content_headers, server_set_encoding_headers, remove_headers
from Headers import has_header_value, WcMessage
from wc import i18n, config
from wc.log import *
from ClientServerMatchmaker import serverpool
from wc.filter import applyfilter, initStateObjects, FilterWait, FilterPics
from wc.filter import FILTER_RESPONSE
from wc.filter import FILTER_RESPONSE_HEADER
from wc.filter import FILTER_RESPONSE_DECODE
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter import FILTER_RESPONSE_ENCODE


# DEBUGGING
PRINT_SERVER_HEADERS = 0
SPEEDCHECK_START = time.time()
SPEEDCHECK_BYTES = 0

_RESPONSE_FILTERS = (
   FILTER_RESPONSE_DECODE,
   FILTER_RESPONSE_MODIFY,
   FILTER_RESPONSE_ENCODE)


is_http_status = re.compile(r'^\d\d\d$').search
def get_response_data (response, url):
    """parse a response status line into tokens (protocol, status, msg)"""
    parts = response.split(None, 2)
    if len(parts)==2:
        warn(PROXY, "Empty response message from %s", `url`)
        parts += ['Bummer']
    elif len(parts)!=3:
        error(PROXY, "Invalid response %s from %s", `response`, `url`)
        parts = ['HTTP/1.0', 200, 'Ok']
    if not is_http_status(parts[1]):
        error(PROXY, "Invalid http statuscode %s from %s", parts[1], `url`)
        parts[1] = 200
    parts[1] = int(parts[1])
    return parts


class HttpServer (Server):
    """HttpServer handles the connection between the proxy and a http server.
     It writes the client request to the server and sends answer data back
     to the client connection object, which is in most cases a HttpClient,
     but could also be a HttpProxyClient (for Javascript sources)
    """
    def __init__ (self, ipaddr, port, client):
        super(HttpServer, self).__init__(client, 'connect')
        self.addr = (ipaddr, port)
        self.hostname = ''
        self.document = ''
        self.response = ''
        self.headers = {}
        self.data_written = False
        self.decoders = [] # Handle each of these, left to right
        self.sequence_number = 0 # For persistent connections
        self.attrs = {} # initial filter attributes are empty
        self.persistent = False
        self.flushing = False
        self.authtries = 0
        self.statuscode = None
        self.bytes_remaining = None
        # attempt connect
        create_inet_socket(self, socket.SOCK_STREAM)
        try:
	    self.connect(self.addr)
        except socket.error:
            self.handle_error('connect error')


    def __repr__ (self):
        extra = self.request()
        if self.client:
            extra += " client"
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('server', self.state, extra)


    def writable (self):
        # It's writable if we're connecting .. TODO: move this
        # logic into the Connection class
        return self.state == 'connect' or self.send_buffer != ''


    def request (self):
        if self.addr[1] != 80:
	    portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        return '%s%s%s' % (self.hostname or self.addr[0],
                           portstr, self.document)


    def process_connect (self):
        assert self.state == 'connect'
        self.state = 'client'
        if self.client:
            # We have to delay this because we haven't gone through the
            # handle_connect completely, and the client expects us to
            # be fully connected when it is notified.  After the
            # delay, the client might be gone.  Example: the connection
            # times out, and it calls handle_connect, then handle_write.
            # The handle_write notices the error, so it disconnects us
            # from the client.  THEN the timer runs and we can't say
            # we've connected, because we really haven't.  XXX: we
            # really should hide these sorts of cases inside Connection.
            make_timer(0, lambda s=self: s.client and s.client.server_connected(s))
        else:
            # Hm, the client no longer cares about us, so close
            self.reuse()


    def client_send_request (self, method, hostname, document, headers,
                            content, client, nofilter, url, mime):
        """the client (matchmaker) sends the request to the server"""
        assert self.state == 'client'
        self.client = client
        self.method = method
        self.hostname = hostname
        self.document = document
        self.content = content
        self.nofilter = nofilter
        self.url = url
        # fix mime content-type for eg JavaScript
        self.mime = mime
        # remember client header for authorization resend
        self.clientheaders = headers
        if config['parentproxycreds']:
            # stored previous proxy authentication (for Basic and Digest auth)
            headers['Proxy-Authorization'] = "%s\r"%config['parentproxycreds']
        self.send_request()


    def send_request (self):
        """actually send the request to the server, is also used to
        send a request twice for NTLM authentication"""
        request = '%s %s HTTP/1.1\r\n' % (self.method, self.document)
        debug(PROXY, '%s write request\n%s', str(self), `request`)
        self.write(request)
        debug(PROXY, "%s write headers\n%s", str(self), str(self.clientheaders))
        self.write("".join(self.clientheaders.headers))
        self.write('\r\n')
        self.write(self.content)
        self.state = 'response'


    def process_read (self):
        assert self.state not in ('connect', 'client'), \
            'server should not receive data in %s state'%self.state

        while True:
            if not self.client:
                # By the time this server object was ready to receive
                # data, the client has already closed the connection!
                # We never received the client_abort because the server
                # didn't exist back when the client aborted.
                self.client_abort()
                return
            bytes_before = len(self.recv_buffer)
            state_before = self.state
            try:
                handler = getattr(self, 'process_'+self.state)
            except AttributeError:
                pass # NO-OP
            handler()
            bytes_after = len(self.recv_buffer)
            state_after = self.state
            if self.client is None or \
               (bytes_before==bytes_after and state_before==state_after):
                break


    def process_response (self):
        i = self.recv_buffer.find('\n')
        if i < 0: return
        self.response = self.read(i+1).strip()
        if self.response.lower().startswith('http'):
            # Okay, we got a valid response line
            protocol, self.statuscode, tail = get_response_data(self.response, self.url)
            # reconstruct cleaned response
            self.response = "%s %d %s" % (protocol, self.statuscode, tail)
            self.state = 'headers'
            # Let the server pool know what version this is
            serverpool.set_http_version(self.addr, get_http_version(protocol))
        elif not self.response:
            # It's a blank line, so assume HTTP/0.9
            serverpool.set_http_version(self.addr, (0,9))
            self.statuscode = 200
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	                   WcMessage(StringIO('')), attrs=self.nofilter)
            self.decoders = []
            self.attrs['nofilter'] = self.nofilter['nofilter']
            # initStateObject can modify headers (see Compress.py)!
            if self.attrs['nofilter']:
                self.attrs = self.nofilter
            else:
                self.attrs = initStateObjects(self.headers, self.url)
            wc.proxy.HEADERS.append((self.url, "server", self.headers))
            self.state = 'content'
            self.client.server_response(self.response, self.statuscode, self.headers)
        else:
            # the HTTP line was missing, just assume that it was there
            # Example: http://ads.adcode.de/frame?11?3?10
            warn(PROXY, i18n._('invalid or missing response from %s: %s'),
                 self.url, `self.response`)
            serverpool.set_http_version(self.addr, (1,0))
            # put the read bytes back to the buffer and fix the response
            self.recv_buffer = self.response + self.recv_buffer
            self.response = "HTTP/1.0 200 Ok"
            self.statuscode = 200
            self.state = 'headers'
        if self.response:
            self.response = applyfilter(FILTER_RESPONSE, self.response,
                              attrs=self.nofilter).strip()
        debug(PROXY, "%s response %s", str(self), `self.response`)


    def process_headers (self):
        # Headers are terminated by a blank line .. now in the regexp,
        # we want to say it's either a newline at the beginning of
        # the document, or it's a lot of headers followed by two newlines.
        # The cleaner alternative would be to read one line at a time
        # until we get to a blank line...
        m = re.match(r'^((?:[^\r\n]+\r?\n)*\r?\n)', self.recv_buffer)
        if not m: return
        # get headers
        fp = StringIO(self.read(m.end()))
        msg = WcMessage(fp)
        # put unparsed data (if any) back to the buffer
        msg.rewindbody()
        self.recv_buffer = fp.read() + self.recv_buffer
        debug(PROXY, "%s server headers\n%s", str(self), str(msg))
        if self.statuscode==100:
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        http_ver = serverpool.http_versions[self.addr]
        if http_ver >= (1,1):
            self.persistent = not has_header_value(msg, 'Connection', 'Close')
        elif http_ver >= (1,0):
            self.persistent = has_header_value(msg, 'Connection', 'Keep-Alive')
        else:
            self.persistent = False
        # filter headers
        try:
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
                                       msg, attrs=self.nofilter)
        except FilterPics, msg:
            self.statuscode = 403
            debug(PROXY, "%s FilterPics %s", str(self), `msg`)
            # XXX get version
            response = "HTTP/1.1 403 Forbidden"
            headers = WcMessage(StringIO('Content-type: text/plain\r\n'
                        'Content-Length: %d\r\n\r\n' % len(msg)))
            self.client.server_response(response, self.statuscode, headers)
            self.client.server_content(msg)
            self.client.server_close()
            self.state = 'recycle'
            self.reuse()
            return
        server_set_headers(self.headers)
        self.bytes_remaining = server_set_encoding_headers(self.headers, self.is_rewrite(), self.decoders, self.client.compress, self.bytes_remaining)
        # 304 Not Modified does not send any type info, because it was cached
        if self.statuscode!=304:
            server_set_content_headers(self.headers, self.document, self.mime, self.url)
        self.attrs['nofilter'] = self.nofilter['nofilter']
        # initStateObject can modify headers (see Compress.py)!
        if self.attrs['nofilter']:
            self.attrs = self.nofilter
        else:
            self.attrs = initStateObjects(self.headers, self.url)
        # XXX <doh>
        #if not self.headers.has_key('Content-Length'):
        #    self.headers['Connection'] = 'close\r'
        #remove_headers(self.headers, ['Keep-Alive'])
        # XXX </doh>
        wc.proxy.HEADERS.append((self.url, "server", self.headers))
        if self.statuscode!=407:
            self.client.server_response(self.response, self.statuscode, self.headers)
        if self.statuscode in (204, 304) or self.method == 'HEAD':
            # These response codes indicate no content
            self.state = 'recycle'
        else:
            self.state = 'content'


    def is_rewrite (self):
        for ro in config['mime_content_rewriting']:
            if ro.match(self.headers.get('Content-Type', '')):
                return True
        return False


    def process_content (self):
        data = self.read(self.bytes_remaining)
        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)
            debug(PROXY, "%s %d bytes remaining", str(self), self.bytes_remaining)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        try:
            for i in _RESPONSE_FILTERS:
                data = applyfilter(i, data, attrs=self.attrs)
            if data:
                if self.statuscode!=407:
                    self.client.server_content(data)
                self.data_written = True
        except FilterWait, msg:
            debug(PROXY, "%s FilterWait %s", str(self), `msg`)
        except FilterPics, msg:
            debug(PROXY, "%s FilterPics %s", str(self), `msg`)
            assert not self.data_written
            # XXX interactive options here
            self.client.server_content(str(msg))
            self.client.server_close()
            self.state = 'recycle'
            self.reuse()
            return
        underflow = self.bytes_remaining is not None and \
                   self.bytes_remaining < 0
        if underflow:
            warn(PROXY, i18n._("server received %d bytes more than content-length"),
                 (-self.bytes_remaining))
        if is_closed or self.bytes_remaining==0:
            # Either we ran out of bytes, or the decoder says we're done
            self.state = 'recycle'


    def process_recycle (self):
        debug(PROXY, "%s recycling", str(self))
        if self.statuscode==407 and config['parentproxy']:
            debug(PROXY, "%s need parent proxy authentication", str(self))
            if self.authtries:
                # we failed twice, abort
                self.authtries = 0
                self.handle_error('authentication error')
                config['parentproxycreds'] = None
                return
            self.authtries += 1
            challenges = get_header_challenges(self.headers, 'Proxy-Authenticate')
            remove_headers(self.headers, ['Proxy-Authentication'])
            attrs = {'password_b64': config['parentproxypass'],
                     'username': config['parentproxyuser']}
            if 'NTLM' in challenges:
                attrs['type'] = challenges['NTLM'][0]['type']+1
                # must use GET for ntlm handshake
                if self.method!='GET':
                    self.oldmethod = self.method
                    self.method = 'GET'
            if 'Digest' in challenges:
                # note: assume self.document is already url-encoded
                attrs['uri'] = get_auth_uri(self.document)
                # with https, this is CONNECT
                attrs['method'] = self.method
                attrs['requireExtraQuotes'] = self.headers.get('Server', '').lower().startswith('microsoft-iis')
            creds = get_credentials(challenges, **attrs)
            # resubmit the request with proxy credentials
            self.state = 'client'
            config['parentproxycreds'] = creds
            self.clientheaders['Proxy-Authorization'] = "%s\r" % creds
            self.send_request()
        else:
            # flush pending client data and try to reuse this connection
            self.flush()


    def flush (self):
        """flush data of decoders (if any) and filters"""
        debug(PROXY, "%s flushing", str(self))
        self.flushing = True
        data = ""
        while self.decoders:
            data = self.decoders[0].flush()
            del self.decoders[0]
            for decoder in self.decoders:
                data = decoder.decode(data)
        try:
            for i in _RESPONSE_FILTERS:
                data = applyfilter(i, data, fun="finish", attrs=self.attrs)
        except FilterWait, msg:
            debug(PROXY, "%s FilterWait %s", str(self), `msg`)
            # the filter still needs some data so try flushing again
            # after a while
            make_timer(0.2, lambda : self.flush())
            return
        # the client might already have closed
        if self.client and self.statuscode!=407:
            if data:
                self.client.server_content(data)
            self.client.server_close()
        self.attrs = {}
        if self.statuscode!=407:
            self.reuse()


    def reuse (self):
        debug(PROXY, "%s reuse", str(self))
        self.client = None
        if self.connected and self.persistent:
            debug(PROXY, '%s reusing %d', str(self), self.sequence_number)
            self.sequence_number += 1
            self.state = 'client'
            self.document = ''
            self.statuscode = None
            self.flushing = False
            # Put this server back into the list of available servers
            serverpool.unreserve_server(self.addr, self)
        else:
            # We can't reuse this connection
            self.close()


    def close (self):
        debug(PROXY, "%s close", str(self))
        if self.connected and self.state!='closed':
            serverpool.unregister_server(self.addr, self)
            self.state = 'closed'
        super(HttpServer, self).close()


    def handle_error (self, what):
        super(HttpServer, self).handle_error(what)
        if self.client:
            client, self.client = self.client, None
            client.server_abort()


    def handle_close (self):
        debug(PROXY, "%s handle_close", str(self))
        self.persistent = False
        super(HttpServer, self).handle_close()
        # flush unhandled data
        if not self.flushing:
            self.flush()
        if self.authtries>0:
            self.reconnect()


    def reconnect (self):
        debug(PROXY, "%s reconnect", str(self))
        # we still must have the client connection
        if not self.client:
            error(PROXY, "%s lost client on reconnect", str(self))
            return
        from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
        # note: self.client still the matchmaker object
        client = self.client.client
        client.state = 'request'
        self.client = None
        ClientServerMatchmaker(client, client.request,
                               self.clientheaders, # with new auth
                               client.content, client.nofilter,
                               client.compress)


def speedcheck_print_status ():
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        debug(PROXY, 'speed: %4d b/s', (SPEEDCHECK_BYTES/elapsed))
        pass
    SPEEDCHECK_START = time.time()
    SPEEDCHECK_BYTES = 0
    make_timer(5, speedcheck_print_status)
    #if serverpool.map:
    #    print 'server pool:'
    #    for addr,set in serverpool.map.items():
    #        for server,status in set.items():
    #            print '  %15s:%-4d %10s %s' % (addr[0], addr[1],
    #                                          status[0], server.hostname)

import wc
