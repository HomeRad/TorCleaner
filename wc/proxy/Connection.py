# -*- coding: iso-8859-1 -*-
"""connection handling"""

# asyncore problem -- we can't separately register for reading/writing
# (less efficient: it calls writable(), readable() a LOT)
# (however, for the proxy it may not be a big deal)


import socket
import errno
import wc
import wc.proxy.Dispatcher


# *_BUFSIZE values are critical: setting them too low produces a lot of
# applyfilter() calls with very few data
# setting them too high produces lags if bandwidth is low
# default values are in bytes
SEND_BUFSIZE = 4096
RECV_BUFSIZE = 4096

# to prevent DoS attacks, specify a maximum buffer size
MAX_BUFSIZE = 1024*1024


class Connection (wc.proxy.Dispatcher.Dispatcher):
    """add buffered input and output capabilities"""

    def __init__(self, sock=None):
        """initialize buffers"""
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
        """return True if connection is readable"""
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
        wc.log.debug(wc.LOG_PROXY, '%s Connection.handle_read', self)
        if len(self.recv_buffer) > MAX_BUFSIZE:
            wc.log.warn(wc.LOG_PROXY, '%s read buffer full', self)
            return
        try:
            data = self.recv(RECV_BUFSIZE)
        except socket.error, err:
            if err == errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            wc.log.debug(wc.LOG_PROXY, "%s closed, got empty data", self)
            self.persistent = False
            return
        wc.log.debug(wc.LOG_NET, '%s <= read %d', self, len(data))
        wc.log.debug(wc.LOG_NET, 'data %r', data)
        self.recv_buffer += data
        self.process_read()


    def process_read (self):
        """handle read event"""
        raise NotImplementedError("must be implemented in a subclass")


    def writable (self):
        """return True if connection is writable"""
        return (not self.connected) or self.send_buffer


    def write (self, data):
        """write data to the internal buffer"""
        self.send_buffer += data


    def handle_write (self):
        """Write data from send_buffer to connection socket.
           Execute a possible pending close."""
        assert self.connected
        assert self.send_buffer
        wc.log.debug(wc.LOG_PROXY, '%s handle_write', self)
        num_sent = 0
        data = self.send_buffer[:SEND_BUFSIZE]
        try:
            num_sent = self.send(data)
        except socket.error, err:
            if err == errno.EAGAIN:
                # try again later
                return
            self.handle_error(str(err))
            return
        wc.log.debug(wc.LOG_NET, '%s => wrote %d', self, num_sent)
        wc.log.debug(wc.LOG_NET, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()


    def handle_connect (self):
        """empty function; per default we don't connect to anywhere"""
        pass


    def close (self):
        """close connection"""
        wc.log.debug(wc.LOG_PROXY, '%s Connection.close', self)
        self.close_pending = False
        if self.persistent:
            self.close_reuse()
        else:
            self.close_close()


    def close_close (self):
        """close the connection socket"""
        wc.log.debug(wc.LOG_PROXY, '%s Connection.close_close', self)
        if self.connected:
            self.connected = False
            super(Connection, self).close()


    def handle_close (self):
        """if we are still connected, wait until all data is sent, then close
           otherwise just close"""
        wc.log.debug(wc.LOG_PROXY, "%s Connection.handle_close", self)
        if self.connected:
            self.delayed_close()
        else:
            self.close()


    def close_ready (self):
        """return True if all data is sent and this connection can be closed
        """
        return not self.send_buffer


    def delayed_close (self):
        """Close whenever the data has been sent"""
        assert self.connected
        wc.log.debug(wc.LOG_PROXY, '%s Connection.delayed_close', self)
        if not self.close_ready():
            # We can't close yet because there's still data to send
            wc.log.debug(wc.LOG_PROXY, '%s close ready channel', self)
            self.close_pending = True
        else:
            self.close()


    def close_reuse (self):
        """don't close the socket, just reset the connection state.
           Must only be called for persistent connections"""
        assert self.persistent
        assert self.connected
        wc.log.debug(wc.LOG_PROXY, '%s Connection.close_reuse %d', self, self.sequence_number)
        self.sequence_number += 1


    def handle_error (self, what):
        """print error and close the connection"""
        wc.log.debug(wc.LOG_PROXY, "%s error %s", self, what)
        super(Connection, self).handle_error(what)
        self.close()


    def handle_expt (self):
        """print exception"""
        wc.log.exception(wc.LOG_PROXY, "%s exception", self)
