import time, socket, rfc822, re, sys, mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'bzip'

from cStringIO import StringIO
from Server import Server
from wc.proxy import make_timer
from wc import debug, config, remove_headers, _
from wc.debug_levels import *
from ClientServerMatchmaker import serverpool
from UnchunkStream import UnchunkStream
from GunzipStream import GunzipStream
from DeflateStream import DeflateStream
from wc.filter import applyfilter, initStateObjects
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

# http request matcher
_http_re = re.compile(r'(?i).*HTTP/(\d+\.?\d*)\s*$')

_fix_content_types = [
    'text/html',
]

class HttpServer (Server):
    def __init__ (self, ipaddr, port, client):
        Server.__init__(self, client)
        self.addr = (ipaddr, port)
        self.hostname = ''
        self.document = ''
        self.response = ''
        self.headers = None
        self.decoders = [] # Handle each of these, left to right
        self.sequence_number = 0 # For persistent connections
        self.attrs = {} # initial filter attributes are empty
        self.attempt_connect()


    def __repr__ (self):
        extra = self.request()
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('server', self.state, extra)


    def writable (self):
        # It's writable if we're connecting .. TODO: move this
        # logic into the Connection class
        return self.state == 'connect' or self.send_buffer != ''


    def request (self):
        if self.addr[1] != 80:
	    portstr = ':%s' % self.addr[1]
        else:
            portstr = ''
        return '%s%s%s' % (self.hostname or self.addr[0],
                           portstr, self.document)


    def attempt_connect (self):
        self.state = 'connect'
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
	    self.connect(self.addr)
        except socket.error, err:
            self.handle_error('connect error', socket.error, err)
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


    def send_request (self):
        self.write('%s %s HTTP/1.1\r\n' % (self.method, self.document))
        for header in self.client.headers.headers:
            self.write(header)
        if not self.client.headers.has_key('Connection'):
            self.write('Connection: Keep-Alive\r\n')
        self.write('\r\n')
        self.write(self.content)
        self.state = 'response'


    def client_send_request (self, method, hostname, document, headers,
                            content, client, nofilter, url):
        assert self.state == 'client'
        self.client = client
        self.method = method
        self.hostname = hostname
        self.document = document
        self.content = content
        self.nofilter = nofilter
        self.url = url
        self.send_request()


    def process_read (self):
        assert self.state not in ('connect', 'client'), \
            ('server should not receive data in %s state'%self.state)

        while "True":
            if not self.client:
                # By the time this server object was ready to receive
                # data, the client has already closed the connection!
                # We never received the client_abort because the server
                # didn't exist back when the client aborted.
                self.client_abort()
                return
            bytes_before = len(self.recv_buffer)
            state_before = self.state
            try: handler = getattr(self, 'process_'+self.state)
            except AttributeError: handler = lambda:None # NO-OP
            handler()
            bytes_after = len(self.recv_buffer)
            if (self.client is None or
                (bytes_before==bytes_after and state_before==self.state)):
                break


    def process_response (self):
        i = self.recv_buffer.find('\n')
        if i < 0: return
        self.response = applyfilter(FILTER_RESPONSE, self.read(i+1),
	                attrs=self.nofilter)
        if self.response.lower().find('http') >= 0:
            # Okay, we got a valid response line
            self.state = 'headers'
            # Let the server pool know what version this is
            serverpool.set_http_version(self.addr, self.http_version())
        elif not self.response.strip():
            # It's a blank line, so assume HTTP/0.9
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	                   rfc822.Message(StringIO('')), attrs=self.nofilter)
            self.bytes_remaining = None
            self.decoders = []
            self.attrs = initStateObjects(self.headers, self.url)
            self.attrs['nofilter'] = self.nofilter['nofilter']
            self.state = 'content'
            self.client.server_response(self.response, self.headers)
        else:
            # We have no idea what it is!?
            print >> sys.stderr, \
                    _('Warning: puzzling header received from host %s:') % \
                    self.hostname, `self.response`



    def process_headers (self):
        # Headers are terminated by a blank line .. now in the regexp,
        # we want to say it's either a newline at the beginning of
        # the document, or it's a lot of headers followed by two newlines.
        # The cleaner alternative would be to read one line at a time
        # until we get to a blank line...
        m = re.match(r'^((?:[^\r\n]+\r?\n)*\r?\n)', self.recv_buffer)
        if not m: return
        # handle continue requests (XXX should be in process_response?)
        response = self.response.split()
        if response and response[1] == '100':
            # it's a Continue request, so go back to waiting for headers
            # XXX for HTTP/1.1 clients, forward this
            self.state = 'response'
            return
        # filter headers
        self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	               rfc822.Message(StringIO(self.read(m.end()))),
		       attrs=self.nofilter)
        #debug(HURT_ME_PLENTY, "S/Headers", `self.headers.headers`)
        # check content-type against our own guess
        gm = mimetypes.guess_type(self.document, None)
        if gm[0]:
            # guessed an own content type
            if not self.headers.has_key('Content-Type'):
                self.headers['Content-Type'] = gm[0]
                print >>sys.stderr, _("Warning: %s guessed Content-Type (%s)") % \
                                      (self.url, gm[0])
           # fix some content types
            elif self.headers.get('Content-Type') != gm[0] and \
                 gm[0] in _fix_content_types:
                print >>sys.stderr, _("Warning: %s guessed Content-Type (%s) != server Content-Type (%s)") % \
                          (self.url, gm[0], self.headers.get('Content-Type'))
                self.headers['Content-Type'] = gm[0]
        if gm[1]:
            # guessed an own encoding type
            if not self.headers.has_key('Content-Encoding'):
                self.headers['Content-Encoding'] = gm[1]
                print >>sys.stderr, _("Warning: %s guessed Content-Encoding (%s)") % \
                                      (self.url, gm[1])
            elif self.headers.get('Content-Encoding') != gm[1]:
                print >>sys.stderr, _("Warning: %s guessed Content-Encoding (%s) != server Content-Encoding (%s)") % \
                                      (self.url, gm[1], self.headers.get('Content-Encoding'))
                self.headers['Content-Encoding'] = gm[1]
        # will content be rewritten?
        rewrite = None
        for ro in config['mime_content_rewriting']:
            if ro.match(self.headers.get('Content-Type', '')):
                rewrite = "True"
                break
        # add client accept-encoding value
        self.headers['Accept-Encoding'] = self.client.compress
        if self.headers.has_key('Content-Length'):
            self.bytes_remaining = int(self.headers['Content-Length'])
            #debug(HURT_ME_PLENTY, "%d bytes remaining"%self.bytes_remaining)
            if rewrite:
                remove_headers(self.headers, ['Content-Length'])
        else:
            self.bytes_remaining = None

        # add decoders
        self.decoders = []

        # Chunked encoded
        if self.headers.has_key('Transfer-Encoding'):
            #debug(BRING_IT_ON, 'S/Transfer-encoding:', `self.headers['transfer-encoding']`)
            self.decoders.append(UnchunkStream())
            # remove encoding header
            to_remove = ["Transfer-Encoding"]
            if self.headers.has_key("Content-Length"):
                print >>sys.stderr, _('Warning: chunked encoding should not have Content-Length')
                to_remove.append("Content-Length")
                self.bytes_remaining = None
            remove_headers(self.headers, to_remove)
            # add warning
            self.headers['Warning'] = "214 WebCleaner Transformation applied"
        # Compressed content (uncompress only for rewriting modules)
        encoding = self.headers.get('Content-Encoding', '').lower()
        if encoding in ('gzip', 'x-gzip', 'deflate') and rewrite:
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
            self.headers['Warning'] = "214 WebCleaner Transformation applied"
        elif encoding and encoding!='identity' and rewrite:
            print >>sys.stderr, _("Warning: unsupported encoding:"),`encoding`
            # do not disable filtering for unknown content-encodings
            # this could result in a DoS attack (server sending garbage
            # as content-encoding)
        # initStateObject can modify headers (see Compress.py)!
        self.attrs = initStateObjects(self.headers, self.url)
        if not self.headers.has_key('Content-Length'):
            self.headers['Connection'] = 'close'
        #debug(HURT_ME_PLENTY, "S/Headers filtered", `self.headers.headers`)
        wc.proxy.HEADERS.append((self.url, 1, self.headers.headers))
        self.client.server_response(self.response, self.headers)
        self.attrs['nofilter'] = self.nofilter['nofilter']
        if ((response and response[1] in ('204', '304')) or \
           self.method == 'HEAD'):
            # These response codes indicate no content
            self.state = 'recycle'
        else:
            self.state = 'content'


    def process_content (self):
        data = self.read(self.bytes_remaining)
        #debug(NIGHTMARE, "S/content", `data`)
        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)
            #debug(HURT_ME_PLENTY, "%d bytes remaining"%self.bytes_remaining)
            if self.bytes_remaining < 0:
                print >>sys.stderr, _("Warning: server received %d bytes more than content-length") % (-self.bytes_remaining)
        filtered_data = data
        is_closed = 0
        for decoder in self.decoders:
            filtered_data = decoder.decode(filtered_data)
            is_closed = decoder.closed or is_closed
        for i in _RESPONSE_FILTERS:
            filtered_data = applyfilter(i, filtered_data, attrs=self.attrs)
        if filtered_data:
	    self.client.server_content(filtered_data)
        if (is_closed or
            (self.bytes_remaining is not None and
             self.bytes_remaining <= 0)):
            # Either we ran out of bytes, or the decoder says we're done
            #debug(HURT_ME_PLENTY, "S/contentfinished")
            self.state = 'recycle'


    def process_recycle (self):
        # We're done sending things to the client, and we can reuse
        # this connection
        client = self.client
        self.reuse()
        self.flush(client)


    def flush (self, client):
        """flush data of decoders (if any) and filters"""
        data = ""
        while self.decoders:
            data = self.decoders[0].flush()
            del self.decoders[0]
            for decoder in self.decoders:
                data = decoder.decode(data)
        for i in _RESPONSE_FILTERS:
            data = applyfilter(i, data, fun="finish", attrs=self.attrs)
        if data:
	    client.server_content(data)
        self.attrs = {}
        client.server_close()


    def http_version (self):
        if not self.response: return 0
        version = _http_re.match(self.response)
        if version:
            return float(version.group(1))
        else:
            return 0.9


    def reuse (self):
        if self.http_version() >= 1.1:
            can_reuse = not (self.headers and
                self.headers.get('Connection', '').lower()=='close')
        else:
            can_reuse = self.headers and \
               self.headers.get('Connection', '').lower()=='keep-alive'
        if not can_reuse:
            # We can't reuse this connection
            self.close()
        else:
            #debug(HURT_ME_PLENTY, 'S/recycling', self.sequence_number, self)
            self.sequence_number += 1
            self.state = 'client'
            self.document = ''
            self.client = None
            # Put this server back into the list of available servers
            serverpool.unreserve_server(self.addr, self)


    def close (self):
        #debug(HURT_ME_PLENTY, "S/close", self)
        if self.connected and self.state!='closed':
            serverpool.unregister_server(self.addr, self)
            self.state = 'closed'
        Server.close(self)


    def handle_error (self, what, type, value, tb=None):
        Server.handle_error(self, what, type, value, tb)
        if self.client:
            client, self.client = self.client, None
            client.server_abort()


    def handle_close (self):
        #debug(HURT_ME_PLENTY, "S/handle_close", self)
        Server.handle_close(self)
        if self.client:
            client, self.client = self.client, None
            self.flush(client)


def speedcheck_print_status ():
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        #debug(BRING_IT_ON, 'speed: %4d b/s' % (SPEEDCHECK_BYTES/elapsed))
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
