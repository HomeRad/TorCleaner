import socket, errno
from wc.log import *
from Connection import Connection, MAX_BUFSIZE, RECV_BUFSIZE, SEND_BUFSIZE
from OpenSSL import SSL


class SslConnection (Connection):
    """mix-in class for SSL connections"""
    def handle_read (self):
        """read data from SSL connection, put it into recv_buffer and call
           process_read"""
        assert self.connected
        debug(PROXY, '%s Connection.handle_read', self)
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
        except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError), err:
            exception(PROXY, "%s ssl read message %s", self, err)
            return
        except (SSL.Error, SSL.ZeroReturnError), err:
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            debug(PROXY, "%s closed, got empty data", self)
            return
        debug(CONNECTION, '%s <= read %d', self, len(data))
        debug(CONNECTION, 'data %r', data)
	self.recv_buffer += data
        self.process_read()


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
        except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError), err:
            exception(PROXY, "%s ssl write message %s", self, err)
            return
        except SSL.Error, err:
            self.handle_error('write error')
            return
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('write error')
            return
        debug(CONNECTION, '%s => wrote %d', self, num_sent)
        debug(CONNECTION, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()

