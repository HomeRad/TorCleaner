import time,socket,rfc822,re
from cStringIO import StringIO
from Server import Server
from wc.proxy import make_timer
from wc import debug
from wc.debug_levels import *
from ClientServerMatchmaker import serverpool
from string import find,strip,split,join,lower
from UnchunkStream import UnchunkStream
from GunzipStream import GunzipStream
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


class HttpServer(Server):
    def __init__(self, ipaddr, port, client):
        Server.__init__(self, client)
        self.addr = (ipaddr, port)
        self.hostname = ''
        self.document = ''
        self.response = ''
        self.headers = None
        self.decoders = [] # Handle each of these, left to right
        self.sequence_number = 0 # For persistent connections
        self.attempt_connect()

    def __repr__(self):
        extra = self.request()
        if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('server', self.state, extra)

    def writable(self):
        # It's writable if we're connecting .. TODO: move this
        # logic into the Connection class
        return self.state == 'connect' or self.send_buffer != ''
    
    def request(self):
        portstr = ''
        if self.addr[1] != 80: portstr = ':%s' % self.addr[1]
        return '%s%s%s' % (self.hostname or self.addr[0],
                            portstr, self.document)
    
    def attempt_connect(self):
        self.state = 'connect'
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try: self.connect(self.addr)
        except socket.error, err:
            debug(ALWAYS, 'connect error', err)
            self.handle_error(socket.error, err)
            return

    def handle_connect(self):
        assert self.state == 'connect'
        debug(HURT_ME_PLENTY, 'handle_conn', self)
        self.state = 'client'
        Server.handle_connect(self)

        if self.client:
            # We have to delay this because we haven't gone through the
            # handle_connect completely, and the client expects us to
            # be fully connected when it is notified.  After the
            # delay, the client might be gone.  Example: the connection
            # times out, and it calls handle_connect, then handle_write.
            # The handle_write notices the error, so it disconnects us
            # from the client.  THEN the timer runs and we can't say
            # we've connected, because we really haven't.  NOTE: we
            # really should hide these sorts of cases inside Connection.
            make_timer(0, lambda s=self: s.client and s.client.server_connected(s))
        else:
            # Hm, the client no longer cares about us, so close
            self.reuse()

    def send_request(self):
        self.write('%s %s HTTP/1.1\r\n' % (self.method, self.document))
        for header in self.client.headers.headers:
            self.write(header)
        self.write('Connection: Keep-Alive\r\n') # TODO: modify existing header
        self.write('\r\n')
        self.write(self.content)

        self.state = 'response'
        
    def client_send_request(self, method, hostname, document, headers,
                            content, client):
        assert self.state == 'client'
        
        self.client = client
        self.method = method
        self.hostname = hostname
        self.document = document
        self.content = content

        self.send_request()
        
    def process_response(self):
        i = find(self.recv_buffer, '\n')
        if i < 0: return
        
        self.response = applyfilter(FILTER_RESPONSE, self.read(i+1))
        if find(self.response, 'HTTP') >= 0:
            # Okay, we got a valid response line
            self.state = 'headers'
            # Let the server pool know what version this is
            serverpool.set_http_version(self.addr, self.http_version())
        elif not strip(self.response):
            # It's a blank line, so assume HTTP/0.9
            self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	                   rfc822.Message(StringIO('')))
            self.bytes_remaining = None
            self.decoders = []
            self.state = 'content'
            self.client.server_response(self.response, self.headers)
        else:
            # We have no idea what it is!?
            debug(ALWAYS, 'Warning', 'puzzling header received ',
	           `self.response`)

    def process_headers(self):
        # Headers are terminated by a blank line .. now in the regexp,
        # we want to say it's either a newline at the beginning of
        # the document, or it's a lot of headers followed by two newlines.
        # The cleaner alternative would be to read one line at a time
        # until we get to a blank line...
        m = re.match(r'^((?:[^\r\n]+\r?\n)*\r?\n)', self.recv_buffer)
        if not m: return
        
        self.headers = applyfilter(FILTER_RESPONSE_HEADER,
	               rfc822.Message(StringIO(self.read(m.end()))))
        if self.headers.has_key('content-length'):
            self.bytes_remaining = int(self.headers.getheader('content-length'))
        else:
            self.bytes_remaining = None
        response = split(self.response)
        if response and response[1] == '100':
            # It's a Continue request, so go back to waiting for
            # headers.
            self.state = 'response'
            return

        if PRINT_SERVER_HEADERS:
            debug(ALWAYS, 'Server headers for http://%s' % self.request())
            debug(ALWAYS, self.response)
            debug(ALWAYS, join(self.headers.headers, '| '))

        self.decoders = []

        if self.headers.has_key('transfer-encoding'):
            debug(BRING_IT_ON, 'Transfer-encoding:',
	          self.headers['transfer-encoding'])
            self.decoders.append(UnchunkStream())
            # HACK - remove encoding header
            for h in self.headers.headers[:]:
                if re.match('transfer-encoding:', lower(h)):
                    self.headers.headers.remove(h)
                elif re.match('content-length:', lower(h)):
                    assert 0, 'chunked encoding should not have content-length'

        if self.headers.has_key('content-encoding') and self.headers['content-encoding'] == 'gzip':
            debug(BRING_IT_ON, 'Content-encoding:', 'gzip')
            self.decoders.append(GunzipStream())
            # HACK - remove content length and encoding
            for h in self.headers.headers[:]:
                if re.match('content-length:', lower(h)):
                    self.headers.headers.remove(h)
                elif re.match('content-encoding:', lower(h)):
                    self.headers.headers.remove(h)

        self.client.server_response(self.response, self.headers)
        if ((response and response[1] in ('204', '304')) or
            self.method == 'HEAD'):
            # These response codes indicate no content
            self.state = 'recycle'
        else:
            mime = self.headers.get('content-type', 'application/octeet-stream')
            self.attrs = initStateObjects(mime, self.headers)
            self.state = 'content'

    def process_content(self):
        debug(NIGHTMARE, "processing server content")
        data = self.read(self.bytes_remaining)

        if self.bytes_remaining is not None:
            # If we do know how many bytes we're dealing with,
            # we'll close the connection when we're done
            self.bytes_remaining -= len(data)

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
            # Either we ran out of bytes, or the filter says we're done
            self.state = 'recycle'

    def process_recycle(self):
        # We're done sending things to the client, and we can reuse
        # this connection
        client = self.client
        self.reuse()

        # Allow each decoder to flush its data, passing it through
        # other decoders
        while self.decoders:
            data = self.decoders[0].flush()
            del self.decoders[0]
            for decoder in self.decoders:
                data = decoder.decode(data)
            for i in _RESPONSE_FILTERS:
                data = applyfilter(i, data, fun="finish", attrs=self.attrs)
            if data: client.server_content(data)

        client.server_close()

    def process_read(self):
        global SPEEDCHECK_BYTES

        if self.state in ('connect', 'client'):
            assert 0, ('server should not receive data in %s state' %
                       self.state)

        while 1:
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
                (bytes_before == bytes_after and state_before == self.state)):
                break

    def http_version(self):
        if not self.response: return 0
        version = re.match(r'.*HTTP/(\d+\.?\d*)\s*$', self.response)
        if version:
            return float(version.group(1))
        else:
            return 0.9
        
    def reuse(self):
        if self.http_version() >= 1.1:
            can_reuse = 1
            if (self.headers and self.headers.has_key('connection') and
                self.headers['connection'] == 'close'):
                can_reuse = 0
        else:
            can_reuse = 0
            if (self.headers and self.headers.has_key('connection') and
                lower(self.headers['connection']) == 'keep-alive'):
                can_reuse = 1
                
        if not can_reuse:
            # We can't reuse this connection
            self.close()
        else:
            debug(HURT_ME_PLENTY, 'recycling', self.sequence_number, self)
            self.sequence_number = self.sequence_number + 1
            self.state = 'client'
            self.document = ''
            self.client = None

            # Put this server back into the list of available servers
            serverpool.unreserve_server(self.addr, self)
        
    def close(self):
        self.state = 'closed'
        Server.close(self)
        serverpool.unregister_server(self.addr, self)

    def handle_error(self, type, value, traceback=None):
        Server.handle_error(self, type, value, traceback)
        if self.client:
            client, self.client = self.client, None
            client.server_abort()
        
    def handle_close(self):
        debug(HURT_ME_PLENTY, 'server close; '+self.state, self)
        Server.handle_close(self)
        if self.client:
            client, self.client = self.client, None
            client.server_close()

def speedcheck_print_status():
    global SPEEDCHECK_BYTES, SPEEDCHECK_START
    elapsed = time.time() - SPEEDCHECK_START
    if elapsed > 0 and SPEEDCHECK_BYTES > 0:
        debug(BRING_IT_ON, 'speed:', '%4d' % (SPEEDCHECK_BYTES/elapsed), 'b/s')
    SPEEDCHECK_START = time.time()
    SPEEDCHECK_BYTES = 0
    make_timer(5, speedcheck_print_status)

    #if serverpool.map:
    #    print 'server pool:'
    #    for addr,set in serverpool.map.items():
    #        for server,status in set.items():
    #            print '  %15s:%-4d %10s %s' % (addr[0], addr[1],
    #                                          status[0], server.hostname)

