import rfc822
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from string import split,find,join
from wc import debug,color
from wc.filter import FILTER_REQUEST
from wc.filter import FILTER_REQUEST_HEADER
from wc.filter import FILTER_REQUEST_DECODE
from wc.filter import FILTER_REQUEST_MODIFY
from wc.filter import FILTER_REQUEST_ENCODE
from wc.filter import applyfilter

class HttpClient(Connection):
    # States:
    # request (read first line)
    # headers (read HTTP headers)
    # data (read any additional data and forward it to the server)
    
    def __init__(self, socket, addr):
        Connection.__init__(self, socket)
        self.addr = addr
        self.state = 'request'
        self.server = None
        self.request = ''
        self.headers = None
        self.bytes_remaining = None # for content only
        self.content = ''

    def __repr__(self):
        if self.state != 'request':
            try: extra = split(self.request)[1][7:] # Remove http://
            except: extra = '???' + self.request
            if len(extra) > 46:
                extra = extra[:43] + '...'
        else:
            extra = 'being read'
        return '<%s:%-8s %s>' % (color(1, 'client'), self.state, extra)

    def process_read(self):
        if self.state == 'request':
            i = find(self.recv_buffer, '\r\n')
            if i >= 0: # One newline ends request
                 # self.read(i) is not including the newline
                self.request = applyfilter(FILTER_REQUEST, self.read(i))
                self.state = 'headers'

        if self.state == 'headers':
            i = find(self.recv_buffer, '\r\n\r\n')
            if i >= 0: # Two newlines ends headers
                i += 4 # Skip over newline terminator
                assert self.read(2) == '\r\n'
                i -= 2 # Skip over newline before headers
                self.headers = applyfilter(FILTER_REQUEST_HEADER,
		               rfc822.Message(StringIO(self.read(i))))
                self.state = 'content'
                if self.headers.has_key('content-length'):
                    self.bytes_remaining = int(self.headers.getheader('content-length'))
                else:
                    self.bytes_remaining = 0

        if self.state == 'content':
	    if self.bytes_remaining > 0:
                # Just pass everything through to the server
                # NOTE: It's possible to have 'chunked' encoding here,
                # and then the current system of counting bytes remaining
                # won't work; we have to deal with chunks
                data = applyfilter(FILTER_REQUEST_DECODE, self.read())
                data = applyfilter(FILTER_REQUEST_MODIFY, data)
                data = applyfilter(FILTER_REQUEST_ENCODE, data)
                self.bytes_remaining -= len(data)
                self.content += data
            else:
                # We're done reading content
                self.state = 'receive'
                # This object will call server_connected at some point
                ClientServerMatchmaker(self, self.request,
                                       self.headers, self.content)

        if self.state in ('receive', 'closed') and self.recv_buffer:
            assert 0, 'client in state %s sent data %s' % \
	              (self.state, `self.recv_buffer`)


    def server_response(self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(NIGHTMARE, 'S/response', self)
        self.write(response)
        self.write(join(headers.headers, ''))
        self.write('\r\n')

    def server_no_response(self):
        debug(NIGHTMARE, 'S/failed', self)
        self.write('**Aborted**')
        self.delayed_close()

    def server_content(self, data):
        assert self.server
        self.write(data)

    def server_close(self):
        assert self.server
        debug(NIGHMARE, 'S/close', self)
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None

    def server_abort(self):
        debug(NIGHTMARE, 'S/abort', self)
        self.close()
        self.server = None
        
    def handle_error(self, type, value, traceback=None):
        # We should also close the server connection
        debug(ALWAYS, 'client error', self, type, value)
        Connection.handle_error(self, type, value, traceback)
        if self.server:
            server, self.server = self.server, None
            server.client_abort()

    def handle_close(self):
        # The client closed the connection, so cancel the server connection
        self.send_buffer = ''
        debug(HURT_ME_PLENTY, 'client close', self)
        Connection.handle_close(self)
        if self.server:
            server, self.server = self.server, None
            server.client_abort()
            # If there isn't a server, then it's in the process of
            # doing DNS lookup or connecting.  The matchmaker will
            # check to see if the client is still connected.

    def close(self):
        self.state = 'closed'
        Connection.close(self)
