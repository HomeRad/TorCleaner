import rfc822,time,sys
from cStringIO import StringIO
from Connection import Connection
from ClientServerMatchmaker import ClientServerMatchmaker
from wc import debug
from wc.proxy import log,match_host
from wc.debug_levels import *
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
            try: extra = self.request.split()[1][7:] # Remove http://
            except: extra = '???' + self.request
            if len(extra) > 46:
                extra = extra[:43] + '...'
        else:
            extra = 'being read'
        return '<%s:%-8s %s>' % ('client', self.state, extra)


    def process_read(self):
        if self.state == 'request':
            i = self.recv_buffer.find('\r\n')
            if i >= 0: # One newline ends request
                # self.read(i) is not including the newline
                self.request = self.read(i)
                self.nofilter = {'nofilter': match_host(self.request)}
                self.request = applyfilter(FILTER_REQUEST, self.request,
                               fun="finish", attrs=self.nofilter)
                log('%s - %s - %s\n' % (self.addr,
		    time.ctime(time.time()), self.request))
                self.state = 'headers'

        if self.state == 'headers':
            i = self.recv_buffer.find('\r\n\r\n')
            if i >= 0: # Two newlines ends headers
                i += 4 # Skip over newline terminator
                assert self.read(2) == '\r\n'
                i -= 2 # Skip over newline before headers
                self.headers = applyfilter(FILTER_REQUEST_HEADER,
		               rfc822.Message(StringIO(self.read(i))),
			       fun="finish", attrs=self.nofilter)
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
                data = self.read()
                self.bytes_remaining -= len(data)
                data = applyfilter(FILTER_REQUEST_DECODE, data,
		                   attrs=self.nofilter)
                data = applyfilter(FILTER_REQUEST_MODIFY, data,
		                   attrs=self.nofilter)
                data = applyfilter(FILTER_REQUEST_ENCODE, data,
		                   attrs=self.nofilter)
                self.content += data
            if self.bytes_remaining <= 0:
                data = applyfilter(FILTER_REQUEST_DECODE, "",
		                   fun="finish", attrs=self.nofilter)
                data = applyfilter(FILTER_REQUEST_DECODE, data,
		                   fun="finish", attrs=self.nofilter)
                data = applyfilter(FILTER_REQUEST_DECODE, data,
		                   fun="finish", attrs=self.nofilter)
                self.content += data
                # We're done reading content
                self.state = 'receive'
                # This object will call server_connected at some point
                ClientServerMatchmaker(self, self.request, self.headers,
		                       self.content, self.nofilter)

        if self.state in ('receive', 'closed') and self.recv_buffer:
            assert 0, 'client in state %s sent data %s' % \
	              (self.state, `self.recv_buffer`)


    def server_response(self, server, response, headers):
        self.server = server
        assert self.server.connected
        #debug(NIGHTMARE, 'S/response', self)
        self.write(response)
        self.write(''.join(headers.headers))
        self.write('\r\n')


    def server_no_response(self):
        #debug(NIGHTMARE, 'S/failed', self)
        self.write('**Aborted**')
        self.delayed_close()


    def server_content(self, data):
        assert self.server
        self.write(data)


    def server_close(self):
        assert self.server
        #debug(NIGHTMARE, 'S/close', self)
        if self.connected and not self.close_pending:
            self.delayed_close()
        self.server = None


    def server_abort(self):
        #debug(NIGHTMARE, 'S/abort', self)
        self.close()
        self.server = None


    def handle_error(self, type, value, tb=None):
        Connection.handle_error(self, 'client error', type, value, tb)
        # We should close the server connection
        if self.server:
            server, self.server = self.server, None
            server.client_abort()


    def handle_close(self):
        # The client closed the connection, so cancel the server connection
        self.send_buffer = ''
        #debug(HURT_ME_PLENTY, 'client close', self)
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
