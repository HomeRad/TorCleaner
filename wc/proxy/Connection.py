# asyncore problem -- we can't separately register for reading/writing
# (less efficient: it calls writable(), readable() a LOT)
# (however, for the proxy it may not be a big deal)  I'd like to
# assume everything is readable, at least.  Is that the case?

# asyncore problem -- suppose we get an error while connecting.
# it calls handle_read_event, and then the recv() gives an exception.
# the problem now is that we can't just close(), because asyncore's
# loop will call handle_write_event, which will then assume the
# connection is reopened(!!!) and then we get another exception
# while trying to write .. argh.  NOTE: I just started using my
# own poll loop to avoid this problem. :P

from wc import message
import asyncore,socket
old_compact_traceback = asyncore.compact_traceback
def new_compact_traceback(a,b,c):
    x,y = old_compact_traceback(a,b,c)
    return x, color(3, str(y))
asyncore.compact_traceback = new_compact_traceback
#del asyncore.dispatcher.__getattr__

RECV_BUFSIZE = 65536
SEND_BUFSIZE = 8192

# XXX implement maximum sizes for buffers to prevent DoS attacks
class Connection(asyncore.dispatcher):
    """add buffered input and output capabilities"""
    def __init__(self, sock=None):
        asyncore.dispatcher.__init__(self, sock)
        self.recv_buffer = ''
        self.send_buffer = ''
        self.close_pending = 0

    def log(self, msg):
        pass

    def close(self):
        if self.connected:
            #message(None, 'close', None, None, self)
            self.connected = 0
            asyncore.dispatcher.close(self)

    def writable(self):
        return len(self.send_buffer)

    def read(self, bytes=RECV_BUFSIZE):
        """read up to LEN bytes from the internal buffer"""
        if bytes is None:
            bytes = RECV_BUFSIZE
        data = self.recv_buffer[:bytes]
        self.recv_buffer = self.recv_buffer[bytes:]
        return data

    def write(self, data):
        """write data to the internal buffer"""
        if self.debug:
            self.log_info('sending %s' % repr(data))
        self.send_buffer += data

    def delayed_close(self):
        "Close whenever the data has been sent"
        assert self.connected
        if self.send_buffer:
            # We can't close yet because there's still data to send
            #message(None, 'close ready', None, None, self)
            self.close_pending = 1
        else:
            self.close()

    # handler functions

    def handle_write(self):
        assert self.connected
        num_sent = 0
        try:
            num_sent = self.send(self.send_buffer[:SEND_BUFSIZE])
        except socket.error, err:
            #message(1, 'write error', None, None, self, err)
            self.handle_error(socket.error, err)
            return
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and not self.send_buffer:
            self.close_pending = 0
            self.close()
        return num_sent

    def handle_connect(self):
        #message(None, 'connect', None, None, self)
        pass

    def handle_read(self):
        if not self.connected:
            # It's been closed (presumably recently)
            #message(0, 'read from connected')
            return
        try:
            data = self.recv(RECV_BUFSIZE)
            if not data: # It's been closed, and handle_close has been called
                return
            #message(None, 'read', len(data), '<=', self)
        except socket.error, err:
            #message(1, 'read error', None, None, self, err)
            self.handle_error(socket.error, err)
            return
	self.recv_buffer += data
        self.process_read()

    def handle_close(self):
        if self.connected:
            self.delayed_close()
        
    def handle_error(self, type, value, tb=None):
        message(1, 'error', None, None, self, type, value)
	import traceback
        if tb: traceback.print_tb(tb)
        if self.connected:
            self.close()
        self.del_channel()
