# -*- coding: iso-8859-1 -*-
# asyncore problem -- we can't separately register for reading/writing
# (less efficient: it calls writable(), readable() a LOT)
# (however, for the proxy it may not be a big deal)

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]


import socket, errno
from wc.log import *
from Dispatcher import Dispatcher

# this is a critical value: setting it too low produces a lot of
# applyfilter() calls with very few data
# setting it too high produces lags if bandwidth is low
RECV_BUFSIZE = 4096
SEND_BUFSIZE = 4096

# to prevent DoS attacks, specify a maximum buffer size
MAX_BUFSIZE = 1024*1024


class Connection (Dispatcher):
    """add buffered input and output capabilities"""
    def __init__(self, sock=None):
        super(Connection, self).__init__(sock)
        self.recv_buffer = ''
        self.send_buffer = ''
        # True if data has still to be written before closing
        self.close_pending = False
        # True if connection should not be closed
        self.persistent = False
        # reuse counter for persistent connections
        self.sequence_number = 0


    def readable (self):
        return self.connected


    def read (self, bytes=RECV_BUFSIZE):
        """read up to LEN bytes from the internal buffer"""
        if bytes is None:
            bytes = RECV_BUFSIZE
        data = self.recv_buffer[:bytes]
        self.recv_buffer = self.recv_buffer[bytes:]
        return data


    def handle_read (self):
        """read data from connection, put it into recv_buffer and call
           process_read"""
        assert self.connected
        debug(PROXY, '%s handle_read', self)
	if len(self.recv_buffer) > MAX_BUFSIZE:
            warn(PROXY, '%s read buffer full', self)
	    return
        try:
            data = self.recv(RECV_BUFSIZE)
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            debug(PROXY, "%s closed, got empty data", self)
            return
        debug(PROXY, '%s <= read %d', self, len(data))
        debug(CONNECTION, 'data %r', data)
	self.recv_buffer += data
        self.process_read()


    def process_read (self):
        raise NotImplementedError("must be implemented in a subclass")


    def writable (self):
        return (not self.connected) or self.send_buffer


    def write (self, data):
        """write data to the internal buffer"""
        self.send_buffer += data


    def handle_write (self):
        """Write data from send_buffer to connection socket.
           Execute a possible pending close."""
        assert self.connected
        assert self.send_buffer
        debug(PROXY, '%s handle_write', self)
        num_sent = 0
        data = self.send_buffer[:SEND_BUFSIZE]
        try:
            num_sent = self.send(data)
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('write error')
            return
        debug(PROXY, '%s => wrote %d', self, num_sent)
        debug(CONNECTION, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()


    def handle_connect (self):
        pass


    def close (self):
        debug(PROXY, '%s close', self)
        self.close_pending = False
        if self.persistent:
            self.close_reuse()
        else:
            self.close_close()


    def close_close (self):
        if self.connected:
            self.connected = False
            super(Connection, self).close()


    def handle_close (self):
        if self.connected:
            self.delayed_close()
        else:
            self.close()


    def close_ready (self):
        return not self.send_buffer


    def delayed_close (self):
        """Close whenever the data has been sent"""
        assert self.connected
        debug(PROXY, '%s delayed_close', self)
        if not self.close_ready():
            # We can't close yet because there's still data to send
            debug(PROXY, '%s close ready channel', self)
            self.close_pending = True
        else:
            self.close()


    def close_reuse (self):
        assert self.persistent
        assert self.connected
        debug(PROXY, '%s reusing %d', self, self.sequence_number)
        self.sequence_number += 1


    def handle_error (self, what):
        exception(PROXY, "%s error %s, closing", self, what)
        self.close()


    def handle_expt (self):
        exception(PROXY, "%s exception", self)
