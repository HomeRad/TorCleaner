# -*- coding: iso-8859-1 -*-
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import asyncore, socket, errno
from wc.log import *

# this is a critical value: setting it too low produces a lot of
# applyfilter() calls with very few data
# setting it too high produces lags if bandwidth is low
RECV_BUFSIZE = 4096
SEND_BUFSIZE = 4096

# to prevent DoS attacks, specify a maximum buffer size
MAX_BUFSIZE = 1024*1024

# XXX drop the ", object" when dispatcher is a new-style class
class Connection (asyncore.dispatcher, object):
    """add buffered input and output capabilities"""
    def __init__(self, sock=None):
        super(Connection, self).__init__(sock)
        self.recv_buffer = ''
        self.send_buffer = ''
        self.close_pending = False


    def read (self, bytes=RECV_BUFSIZE):
        """read up to LEN bytes from the internal buffer"""
        if bytes is None:
            bytes = RECV_BUFSIZE
        data = self.recv_buffer[:bytes]
        self.recv_buffer = self.recv_buffer[bytes:]
        return data


    def handle_read (self):
        if not self.connected:
            # It's been closed (presumably recently)
            return
	if len(self.recv_buffer) > MAX_BUFSIZE:
            warn(PROXY, '%s read buffer full', str(self))
	    return
        try:
            data = self.recv(RECV_BUFSIZE)
        except socket.error, err:
            if err==errno.EAGAIN:
                return
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            return
        debug(PROXY, '%s <= read %d', str(self), len(data))
	self.recv_buffer += data
        self.process_read()


    def process_read (self):
        raise NotImplementedError("must be implemented in a subclass")


    def writable (self):
        return self.send_buffer


    def write (self, data):
        """write data to the internal buffer"""
        self.send_buffer += data


    def handle_write (self):
        assert self.connected
        num_sent = 0
        data = self.send_buffer[:SEND_BUFSIZE]
        if not data:
            warn(PROXY, '%s empty write', str(self))
            return num_sent
        try:
            num_sent = self.send(data)
        except socket.error:
            self.handle_error('write error')
            return
        debug(PROXY, '%s => wrote %d', str(self), num_sent)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and not self.send_buffer:
            self.close_pending = False
            self.close()
        return num_sent


    def handle_connect (self):
        pass


    def close (self):
        if self.connected:
            self.connected = False
            super(Connection, self).close()


    def handle_close (self):
        if self.connected:
            self.delayed_close()


    def delayed_close (self):
        "Close whenever the data has been sent"
        assert self.connected
        if self.send_buffer:
            # We can't close yet because there's still data to send
            debug(PROXY, '%s close ready channel', str(self))
            self.close_pending = True
        else:
            self.close()


    def handle_error (self, what):
        exception(PROXY, "%s error %s, closing", str(self), what)
        self.close()
        self.del_channel()


    def handle_expt (self):
        exception(PROXY, "%s exception", str(self))
