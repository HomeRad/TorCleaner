# -*- coding: iso-8859-1 -*-
# -*- coding: iso-8859-1 -*-
"""connection handling proxy <--> http server"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, socket, re, urlparse, urllib

from cStringIO import StringIO
from Server import Server
from wc.proxy import make_timer, get_http_version, create_inet_socket
from wc.proxy.auth import *
from Headers import server_set_headers, server_set_content_headers, server_set_encoding_headers, remove_headers
from Headers import has_header_value, WcMessage, get_content_length
from wc import i18n, config
from wc.log import *
from ServerPool import serverpool
from wc.filter import applyfilter, get_filterattrs, FilterWait, FilterRating
from wc.filter import FILTER_RESPONSE
from wc.filter import FILTER_RESPONSE_HEADER
from wc.filter import FILTER_RESPONSE_DECODE
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter import FILTER_RESPONSE_ENCODE
from wc.filter.Rating import MISSING

# DEBUGGING
PRINT_SERVER_HEADERS = 0
SPEEDCHECK_START = time.time()
SPEEDCHECK_BYTES = 0

_response_filters = [
    FILTER_RESPONSE_DECODE,
    FILTER_RESPONSE_MODIFY,
    FILTER_RESPONSE_ENCODE,
]

is_http_status = re.compile(r'^\d\d\d$').search
def get_response_data (response, url):
    """parse a response status line into tokens (protocol, status, msg)"""
    parts = response.split(None, 2)
    if len(parts)==2:
        warn(PROXY, "Empty response message from %r", url)
        parts += ['Bummer']
    elif len(parts)!=3:
        error(PROXY, "Invalid response %r from %r", response, url)
        parts = ['HTTP/1.0', 200, 'Ok']
    if not is_http_status(parts[1]):
        error(PROXY, "Invalid http statuscode %r from %r", parts[1], url)
        parts[1] = 200
    parts[1] = int(parts[1])
    return parts


def flush_decoders (decoders):
    data = ""
    while decoders:
        debug(PROXY, "flush decoder %s", decoders[0])
        data = decoders[0].flush()
        del decoders[0]
        for decoder in decoders:
            data = decoder.decode(data)
    return data


class HttpServer (Server):
    """HttpServer handles the connection between the proxy and a http server.
     It writes the client request to the server and sends answer data back
     to the client connection object, which is in most cases a HttpClient,
     but could also be a HttpProxyClient (for Javascript sources)
    """
    def __init__ (self, ipaddr, port, client):
        super(HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.reset()
        # attempt connect
        create_inet_socket(self, socket.SOCK_STREAM)
        self.socket.settimeout(config['timeout'])
        self.connect(self.addr)


    def reset (self):
        self.hostname = ''
        self.method = None
        self.document = ''
        self.response = ''
        self.headers = WcMessage()
        self.decoders = [] # Handle each of these, left to right
        self.persistent = False # for persistent connections
        self.attrs = {'mime': None} # initial filter attributes
        self.authtries = 0 # restrict number of authentication tries
        self.statuscode = None # numeric HTTP status code
        self.bytes_remaining = None # number of content bytes remaining
        self.defer_data = False # for content rating
        debug(PROXY, "%s resetted", self)


    def __repr__ (self):
        """object description"""
        extra = self.persistent and "persistent " or ""
        if self.addr[1] != 80:
	    portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        extra += '%s%s%s' % (self.hostname or self.addr[0],
                             portstr, self.document)
        if self.client:
            extra += " client"
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('server', self.state, extra)


    def process_connect (self):
        """notify client that this server has connected"""
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
            self.close()


    def client_send_request (self, method, protocol, hostname, port,
                             document, headers, content, client, url, mime):
        """the client (matchmaker) sends the request to the server"""
        assert self.state == 'client', "%s invalid state %r"%(self, self.state)
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
        self.mime = mime
        # remember client header for authorization resend
        self.clientheaders = headers
        if self.method!='CONNECT':
            self.mangle_request_headers()
            self.send_request()


    def mangle_request_headers (self):
        if config['parentproxycreds']:
            # stored previous proxy authentication (for Basic and Digest auth)
            self.clientheaders['Proxy-Authorization'] = "%s\r"%config['parentproxycreds']


    def send_request (self):
        """send the request to the server, is also used to send a request
           twice for NTLM authentication"""
        assert self.method!='CONNECT'
        request = '%s %s HTTP/1.1\r\n'%(self.method, self.document)
        debug(PROXY, '%s write request\n%r', self, request)
        self.write(request)
        debug(PROXY, "%s write headers\n%s", self, self.clientheaders)
        self.write("".join(self.clientheaders.headers))
        self.write('\r\n')
        self.write(self.content)
        self.state = 'response'


    def process_read (self):
        """process read event by delegating it to process_* functions"""
        assert self.state!='closed', "%s invalid state %r"%(self, self.state)
        while True:
            if not self.client:
                # By the time this server object was ready to receive
                # data, the client has already closed the connection!
                # We never received the client_abort because the server
                # didn't exist back when the client aborted.
                self.client_abort()
                return
            if self.state=='unreadable':
                return
            if self.delegate_read():
                break


    def process_response (self):
        """look for response line and process it if found"""
        i = self.recv_buffer.find('\n')
        if i < 0:
            return
        self.response = self.read(i+1).strip()
        if self.response.lower().startswith('http'):
            # Okay, we got a valid response line
            protocol, self.statuscode, tail = get_response_data(self.response, self.url)
            # reconstruct cleaned response
            self.response = "%s %d %s" % (self.protocol, self.statuscode, tail)
            self.state = 'headers'
            # Let the server pool know what version this is
            serverpool.set_http_version(self.addr, get_http_version(protocol))
        elif not self.response:
            # It's a blank line, so assume HTTP/0.9
            warn(PROXY, "%s got HTTP/0.9 response", self)
            serverpool.set_http_version(self.addr, (0,9))
            self.response = "%s 200 Ok"%self.protocol
            self.statuscode = 200
            self.attrs = get_filterattrs(self.url, [FILTER_RESPONSE_HEADER])
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	                   WcMessage(), "finish", self.attrs)
            self.decoders = []
            self.state = 'content'
        else:
            # the HTTP line was missing, just assume that it was there
            # Example: http://ads.adcode.de/frame?11?3?10
            warn(PROXY, i18n._('invalid or missing response from %s: %r'),
                 self.url, self.response)
            serverpool.set_http_version(self.addr, (1,0))
            # put the read bytes back to the buffer and fix the response
            self.recv_buffer = self.response + self.recv_buffer
            self.response = "%s 200 Ok"%self.protocol
            self.statuscode = 200
            self.state = 'headers'
        if self.response:
            self.attrs = get_filterattrs(self.url, [FILTER_RESPONSE])
            self.response = applyfilter(FILTER_RESPONSE, self.response,
                                        "finish", self.attrs).strip()
        if self.statuscode >= 400:
            self.mime = None
        debug(PROXY, "%s response %r", self, self.response)


    def process_headers (self):
        """look for headers and process them if found"""
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
        fp.close()
        debug(PROXY, "%s server headers\n%s", self, msg)
        if self.statuscode==100:
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        self.persistent = self.get_persistent(msg, serverpool.http_versions[self.addr])
        self.attrs = get_filterattrs(self.url, [FILTER_RESPONSE_HEADER], headers=msg)
        try:
            self.headers = applyfilter(FILTER_RESPONSE_HEADER, msg,
                                       "finish", self.attrs)
        except FilterRating, msg:
            debug(PROXY, "%s FilterRating from header: %s", self, msg)
            if msg==MISSING:
                # still have to look at content
                self.defer_data = True
            else:
                self._show_rating_deny(str(msg))
                return
        self.mangle_response_headers()
        if self.statuscode in (204, 304) or self.method == 'HEAD':
            # these response codes indicate no content
            self.state = 'recycle'
        else:
            self.state = 'content'
        self.attrs = get_filterattrs(self.url, _response_filters, headers=msg)
        debug(PROXY, "%s filtered headers %s", self, self.headers)
        if not self.defer_data:
            self.client.server_response(self, self.response, self.statuscode,
                                        self.headers)
            # note: self.client could be None here


    def mangle_response_headers (self):
        server_set_headers(self.headers)
        self.bytes_remaining = server_set_encoding_headers(self.headers, self.is_rewrite(), self.decoders, self.bytes_remaining)
        if self.bytes_remaining is None:
            self.persistent = False
        # 304 Not Modified does not send any type info, because it was cached
        if self.statuscode!=304:
            # copy decoders
            decoders = [d.__class__() for d in self.decoders]
            data = self.recv_buffer
            for decoder in decoders:
                data = decoder.decode(data)
            data += flush_decoders(decoders)
            server_set_content_headers(self.headers, data, self.document,
                                       self.mime, self.url)


    def get_persistent (self, headers, http_ver):
        if http_ver >= (1,1):
            persistent = not has_header_value(headers, 'Connection', 'Close')
        elif http_ver >= (1,0):
            persistent = has_header_value(headers, 'Connection', 'Keep-Alive')
        else:
            persistent = False
        return persistent


    def is_rewrite (self):
        """return True iff this server will modify content"""
        for ro in config['mime_content_rewriting']:
            if ro.match(self.headers.get('Content-Type', '')):
                return True
        return False


    def _show_rating_deny (self, msg):
        """requested page is rated"""
        query = urllib.urlencode({"url":self.url, "reason":msg})
        self.statuscode = 302
        response = "%s 302 %s"%(self.protocol, i18n._("Moved Temporarily"))
        headers = WcMessage()
        headers['Content-type'] = 'text/plain\r'
        headers['Location'] = 'http://localhost:%d/rated.html?%s\r'%\
                              (config['port'], query)
        headers['Content-Length'] = '%d\r'%len(msg)
        debug(PROXY, "%s headers\n%s", self, headers)
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
        """process server data: filter it and write it to client"""
        data = self.read(self.bytes_remaining)
        debug(PROXY, "%s process %d bytes", self, len(data))
        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)
            debug(PROXY, "%s %d bytes remaining", self, self.bytes_remaining)
        is_closed = False
        for decoder in self.decoders:
            data = decoder.decode(data)
            debug(PROXY, "%s have run decoder %s", self, decoder)
            if not is_closed and decoder.closed:
                is_closed = True
        try:
            for i in _response_filters:
                data = applyfilter(i, data, "filter", self.attrs)
        except FilterWait, msg:
            debug(PROXY, "%s FilterWait %s", self, msg)
        except FilterRating, msg:
            debug(PROXY, "%s FilterRating from content %s", self, msg)
            self._show_rating_deny(str(msg))
            return
        underflow = self.bytes_remaining is not None and \
                   self.bytes_remaining < 0
        if underflow:
            warn(PROXY, i18n._("server received %d bytes more than content-length"),
                 (-self.bytes_remaining))
        if data and self.statuscode!=407:
            if self.defer_data:
                self.defer_data = False
                self.client.server_response(self, self.response,
                                            self.statuscode, self.headers)
                if not self.client:
                    return
            self.client.server_content(data)
        if is_closed or self.bytes_remaining==0:
            # either we ran out of bytes, or the decoder says we're done
            self.state = 'recycle'


    def process_client (self):
        """gets called on SSL tunneled connections, delegates server data
           directly to the client without filtering"""
        if not self.client:
            # delay
            return
        debug(PROXY, "%s write SSL tunneled data to client %s", self, self.client)
        self.client.write(self.read())


    def process_recycle (self):
        debug(PROXY, "%s recycling", self)
        if self.statuscode==407 and config['parentproxy']:
            debug(PROXY, "%s need parent proxy authentication", self)
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
            self.delayed_close()


    def flush (self):
        """flush data of decoders (if any) and filters and write it to
           the client. return True if flush was successful"""
        debug(PROXY, "%s flushing", self)
        if not self.statuscode:
            warn(PROXY, "%s flush without status", self)
        data = flush_decoders(self.decoders)
        try:
            for i in _response_filters:
                data = applyfilter(i, data, "finish", self.attrs)
        except FilterWait, msg:
            debug(PROXY, "%s FilterWait %s", self, msg)
            # the filter still needs some data
            # to save CPU time make connection unreadable for a while
            self.set_unreadable(0.5)
            return False
        # the client might already have closed
        if self.client and data and self.statuscode!=407:
            self.client.server_content(data)
        return True


    def set_unreadable (self, secs):
        oldstate, self.state = self.state, 'unreadable'
        make_timer(secs, lambda: self.set_readable(oldstate))


    def set_readable (self, state):
        debug(PROXY, "%s set readable", self)
        # the client might already have closed
        if self.client:
            self.state = state
        else:
            debug(PROXY, "%s client is gone", self)


    def close_reuse (self):
        debug(PROXY, "%s HttpServer.close_reuse", self)
        assert not self.client, "reuse with open client"
        super(HttpServer, self).close_reuse()
        self.state = 'client'
        self.reset()
        # be sure to unreserve _after_ reset because of callbacks
        serverpool.unreserve_server(self.addr, self)


    def close_ready (self):
        debug(PROXY, "%s HttpServer.close_ready", self)
        if not (self.client and self.connected):
            # client has lost interest, or we closed already
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
        debug(PROXY, "%s HttpServer.close_close", self)
        assert not self.client, "close with open client"
        unregister = (self.connected and self.state!='closed')
        if unregister:
            self.state = 'closed'
        super(HttpServer, self).close_close()
        if unregister:
            serverpool.unregister_server(self.addr, self)
        assert not self.connected


    def handle_error (self, what):
        debug(PROXY, "%s HttpServer.handle_error", self)
        if self.client:
            client, self.client = self.client, None
            client.server_abort()
        super(HttpServer, self).handle_error(what)


    def handle_close (self):
        debug(PROXY, "%s HttpServer.handle_close", self)
        self.persistent = False
        super(HttpServer, self).handle_close()


    def reconnect (self):
        debug(PROXY, "%s HttpServer.reconnect", self)
        # we still must have the client connection
        if not self.client:
            error(PROXY, "%s lost client on reconnect", self)
            return
        from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
        # note: self.client still the matchmaker object
        client = self.client.client
        client.state = 'request'
        self.client = None
        ClientServerMatchmaker(client, client.request,
                               self.clientheaders, # with new auth
                               client.content, mime=self.mime)


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
