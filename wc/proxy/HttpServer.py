# -*- coding: iso-8859-1 -*-
"""connection handling proxy <--> http server"""
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time, socket, re, mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'

from cStringIO import StringIO
from Server import Server
from wc.proxy import make_timer, get_http_version
from Headers import server_set_headers, remove_headers
from Headers import has_header_value, WcMessage
from wc import i18n, config
from wc.log import *
from ClientServerMatchmaker import serverpool
from UnchunkStream import UnchunkStream
from GunzipStream import GunzipStream
from DeflateStream import DeflateStream
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

_fix_content_types = ['text/html']
_fix_content_encodings = [
#    'x-bzip2',
]

def get_response_data (response):
    """parse a response status line into tokens (protocol, status, msg)"""
    parts = response.split(None, 2)
    if len(parts)==3:
        return parts
    if len(parts)==2:
        return parts[0], parts[1], "Bummer"
    error(PROXY, "Invalid response %s", `response`)
    return "HTTP/1.0", 200, "Ok"


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
        self.attempt_connect()
        self.can_reuse = False
        self.flushing = False
        # proxy challenge for authentication
        self.challenge = None


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


    def attempt_connect (self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
	    self.connect(self.addr)
        except socket.error, err:
            self.handle_error('connect error')
            return


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
            #self.client.server_connected(self)
        else:
            # Hm, the client no longer cares about us, so close
            self.reuse()


    def send_request (self, headers):
        request = '%s %s HTTP/1.1\r\n' % (self.method, self.document)
        self.write(request)
        if hasattr(headers, "headers"):
            # write original Message object headers to preserve
            # case sensitivity (!)
            self.write("".join(headers.headers))
        else:
            for key,val in headers.items():
                header = "%s: %s\r\n" % (key, val.rstrip())
                self.write(header)
        self.write('\r\n')
        self.write(self.content)
        self.state = 'response'


    def client_send_request (self, method, hostname, document, headers,
                            content, client, nofilter, url, mime):
        assert self.state == 'client'
        self.client = client
        self.method = method
        self.hostname = hostname
        self.document = document
        self.content = content
        self.nofilter = nofilter
        self.url = url
        self.mime = mime
        self.send_request(headers)


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
        self.response = applyfilter(FILTER_RESPONSE, self.read(i+1),
	                attrs=self.nofilter).strip()
        if self.response.lower().startswith('http'):
            # Okay, we got a valid response line
            protocol, self.statuscode, tail = get_response_data(self.response)
            self.state = 'headers'
            # Let the server pool know what version this is
            serverpool.set_http_version(self.addr, get_http_version(protocol))
        elif not self.response:
            # It's a blank line, so assume HTTP/0.9
            serverpool.set_http_version(self.addr, (0,9))
            self.statuscode = 200
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	                   WcMessage(StringIO('')), attrs=self.nofilter)
            self.bytes_remaining = None
            self.decoders = []
            self.attrs['nofilter'] = self.nofilter['nofilter']
            # initStateObject can modify headers (see Compress.py)!
            if self.attrs['nofilter']:
                self.attrs = self.nofilter
            else:
                self.attrs = initStateObjects(self.headers, self.url)
            wc.proxy.HEADERS.append((self.url, "server", self.headers))
            self.state = 'content'
            self.client.server_response(self.response, self.headers)
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
        debug(PROXY, "Server: Headers %s", `str(msg)`)
        if self.statuscode == '100':
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        http_ver = serverpool.http_versions[self.addr]
        if http_ver >= (1,1):
            self.can_reuse = not has_header_value(msg, 'Connection', 'Close')
        elif http_ver >= (1,0):
            self.can_reuse = has_header_value(msg, 'Connection', 'Keep-Alive')
        else:
            self.can_reuse = False
        # filter headers
        try:
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
                                       msg, attrs=self.nofilter)
        except FilterPics, msg:
            debug(PROXY, "Server: FilterPics %s", msg)
            # XXX get version
            response = "HTTP/1.0 200 OK"
            headers = {
                "Content-Type": "text/plain",
                "Content-Length": len(msg),
            }
            self.client.server_response(response, headers)
            self.client.server_content(msg)
            self.client.server_close()
            # XXX state?
            self.state = 'recycle'
            self.reuse()
            return
        server_set_headers(self.headers)
        self.check_headers()
        # add encoding specific headers and objects
        self.add_encoding_headers()
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
        debug(PROXY, "Server: Headers filtered %s", `str(self.headers)`)
        wc.proxy.HEADERS.append((self.url, "server", self.headers))
        if config['parentproxy'] and self.statuscode==407:
            self.challenges = get_header_challenges(headers, 'Proxy-Authenticate')
            # resubmit the request with proxy credentials
            # XXX
        self.client.server_response(self.response, self.headers)
        if self.statuscode in ('204', '304') or self.method == 'HEAD':
            # These response codes indicate no content
            self.state = 'recycle'
        else:
            self.state = 'content'



    def check_headers (self):
        """add missing content-type and/or encoding headers"""
        # 304 Not Modified does not send any type or encoding info,
        # because this info was cached
        if self.statuscode == '304':
            return
        # check content-type against our own guess
        i = self.document.find('?')
        if i>0:
            document = self.document[:i]
        else:
            document = self.document
        gm = mimetypes.guess_type(document, None)
        ct = self.headers.get('Content-Type', None)
        if self.mime:
            if ct is None:
                warn(PROXY, i18n._("add Content-Type %s in %s"),
                     `self.mime`, `self.url`)
                self.headers['Content-Type'] = "%s\r"%self.mime
            elif not ct.startswith(self.mime):
                i = ct.find(';')
                if i== -1:
                    val = self.mime
                else:
                    val = self.mime + ct[i:]
                warn(PROXY, i18n._("set Content-Type from %s to %s in %s"),
                     `str(ct)`, `val`, `self.url`)
                self.headers['Content-Type'] = "%s\r"%val
        elif gm[0]:
            # guessed an own content type
            if ct is None:
                warn(PROXY, i18n._("add Content-Type %s to %s"),
                     `gm[0]`, `self.url`)
                self.headers['Content-Type'] = "%s\r"%gm[0]
           # fix some content types
            elif not ct.startswith(gm[0]) and \
                 gm[0] in _fix_content_types:
                warn(PROXY, i18n._("change Content-Type from %s to %s in %s"),
                     `ct`, `gm[0]`, `self.url`)
                self.headers['Content-Type'] = "%s\r"%gm[0]
        if gm[1] and gm[1] in _fix_content_encodings:
            ce = self.headers.get('Content-Encoding', None)
            # guessed an own encoding type
            if ce is None:
                self.headers['Content-Encoding'] = "%s\r"%gm[1]
                warn(PROXY, i18n._("add Content-Encoding %s to %s"),
                     `gm[1]`, `self.url`)
            elif ce != gm[1]:
                warn(PROXY, i18n._("change Content-Encoding from %s to %s in %s"),
                     `ce`, `gm[1]`, `self.url`)
                self.headers['Content-Encoding'] = "%s\r"%gm[1]
        # hmm, fix application/x-httpd-php*
        if self.headers.get('Content-Type', '').lower().startswith('application/x-httpd-php'):
            warn(PROXY, i18n._("fix x-httpd-php Content-Type"))
            self.headers['Content-Type'] = 'text/html\r'


    def add_encoding_headers (self):
        debug(PROXY, "Server: encoding headers %s", blocktext(`str(self.headers)`, 72))
        # will content be rewritten?
        rewrite = self.is_rewrite()
        # add client accept-encoding value
        self.headers['Accept-Encoding'] = "%s\r"%self.client.compress
        if self.headers.has_key('Content-Length'):
            self.bytes_remaining = int(self.headers['Content-Length'])
            debug(PROXY, "Server: %d bytes remaining", self.bytes_remaining)
            if rewrite:
                remove_headers(self.headers, ['Content-Length'])
        else:
            self.bytes_remaining = None
        # add decoders
        self.decoders = []
        # Chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            debug(PROXY, 'Server: Transfer-encoding: %s', `self.headers['Transfer-Encoding']`)
            self.decoders.append(UnchunkStream())
            # remove encoding header
            to_remove = ["Transfer-Encoding"]
            if self.headers.has_key("Content-Length"):
                warn(PROXY, i18n._('chunked encoding should not have Content-Length'))
                to_remove.append("Content-Length")
                self.bytes_remaining = None
            remove_headers(self.headers, to_remove)
            # add warning
            self.headers['Warning'] = "214 Transformation applied\r"
        # only decompress on rewrite
        if not rewrite: return
        # Compressed content (uncompress only for rewriting modules)
        encoding = self.headers.get('Content-Encoding', '').lower()
        # XXX test for .gz files ???
        if encoding in ('gzip', 'x-gzip', 'deflate'):
            if encoding=='deflate':
                self.decoders.append(DeflateStream())
            else:
                self.decoders.append(GunzipStream())
            # remove encoding because we unzip the stream
            to_remove = ['Content-Encoding']
            # remove no-transform cache control
            if self.headers.get('Cache-Control', '').lower()=='no-transform':
                to_remove.append('Cache-Control')
            remove_headers(self.headers, to_remove)
            # add warning
            self.headers['Warning'] = "214 Transformation applied\r"
        elif encoding and encoding!='identity':
            warn(PROXY, i18n._("unsupported encoding: %s"), `encoding`)
            # do not disable filtering for unknown content-encodings
            # this could result in a DoS attack (server sending garbage
            # as content-encoding)


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
            debug(PROXY, "Server: %d bytes remaining", self.bytes_remaining)
        is_closed = False
        debug(PROXY, 'Proxy: server data %s', blocktext(`data`, 72))
        for decoder in self.decoders:
            data = decoder.decode(data)
            is_closed = decoder.closed or is_closed
        debug(PROXY, 'Proxy: server data decoded %s', blocktext(`data`, 72))
        try:
            for i in _RESPONSE_FILTERS:
                data = applyfilter(i, data, attrs=self.attrs)
            if data:
                self.client.server_content(data)
                self.data_written = True
        except FilterWait, msg:
            debug(PROXY, "Server: FilterWait %s", msg)
        except FilterPics, msg:
            debug(PROXY, "Server: FilterPics %s", msg)
            assert not self.data_written
            self.client.server_content(str(msg))
            self.client.server_close()
            # XXX state?
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
        debug(PROXY, "Server: recycling %s", str(self))
        # flush pending client data and try to reuse this connection
        self.flushing = True
        self.flush()


    def flush (self):
        """flush data of decoders (if any) and filters"""
        debug(PROXY, "Server: flushing %s", str(self))
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
            debug(PROXY, "Server: FilterWait %s", msg)
            # the filter still needs some data so try flushing again
            # after a while
            make_timer(0.2, lambda : self.flush())
            return
        # the client might already have closed
        if self.client:
            if data:
                self.client.server_content(data)
            self.client.server_close()
        self.attrs = {}
        self.reuse()


    def reuse (self):
        debug(PROXY, "Server: reuse %s", str(self))
        self.client = None
        if self.connected and self.can_reuse:
            debug(PROXY, 'Server: reusing %d %s', self.sequence_number, str(self))
            self.sequence_number += 1
            self.state = 'client'
            self.document = ''
            self.flushing = False
            # Put this server back into the list of available servers
            serverpool.unreserve_server(self.addr, self)
        else:
            # We can't reuse this connection
            self.close()


    def close (self):
        debug(PROXY, "Server: close %s", str(self))
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
        debug(PROXY, "Server: handle_close %s", str(self))
        self.can_reuse = False
        super(HttpServer, self).handle_close()
        # flush unhandled data
        if not self.flushing:
            self.flush()


def speedcheck_print_status ():
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        debug(PROXY, 'Server: speed: %4d b/s', (SPEEDCHECK_BYTES/elapsed))
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


