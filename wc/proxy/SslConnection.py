# -*- coding: iso-8859-1 -*-
"""
SSL connection, usable for both client and server connections.
"""

import wc
import wc.log
import wc.proxy.Connection
import OpenSSL.SSL


class SslConnection (wc.proxy.Connection.Connection):
    """
    Mix-in class for SSL connections.
    """

    def handle_read (self):
        """
        Read data from SSL connection, put it into recv_buffer and call
        process_read.
        """
        assert self.connected
        wc.log.debug(wc.LOG_PROXY, '%s SslConnection.handle_read', self)
        if len(self.recv_buffer) > wc.proxy.Connection.MAX_BUFSIZE:
            wc.log.warn(wc.LOG_PROXY, '%s read buffer full', self)
            return
        try:
            data = self.socket.read(wc.proxy.Connection.RECV_BUFSIZE)
            wc.log.debug(wc.LOG_NET, 'have read data %r', data)
        except OpenSSL.SSL.WantReadError, err:
            wc.log.debug(wc.LOG_NET, '%s want read error', self)
            # you _are_ already reading, stupid
            return
        except OpenSSL.SSL.WantWriteError, err:
            wc.log.debug(wc.LOG_NET, '%s want write error', self)
            # you want to write? here you go
            self.handle_write()
            return
        except OpenSSL.SSL.WantX509LookupError, err:
            wc.log.exception(wc.LOG_PROXY, "%s ssl read message", self)
            return
        except OpenSSL.SSL.ZeroReturnError, err:
            wc.log.debug(wc.LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except OpenSSL.SSL.Error, err:
            wc.log.exception(wc.LOG_PROXY, "%s read error", self)
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            wc.log.debug(wc.LOG_PROXY, "%s closed, got empty data", self)
            return
        wc.log.debug(wc.LOG_NET, '%s <= read %d', self, len(data))
        self.recv_buffer += data
        self.process_read()

    def handle_write (self):
        """
        Write data from send_buffer to connection socket.
        Execute a possible pending close.
        """
        assert self.connected
        assert self.send_buffer
        wc.log.debug(wc.LOG_PROXY, '%s SslConnection.handle_write', self)
        num_sent = 0
        data = self.send_buffer[:wc.proxy.Connection.SEND_BUFSIZE]
        wc.log.debug(wc.LOG_NET, 'have written data %r', data)
        try:
            num_sent = self.socket.write(data)
        except OpenSSL.SSL.WantReadError, err:
            wc.log.debug(wc.LOG_NET, '%s want read error', self)
            # you want to read? here you go
            self.handle_read()
            return
        except OpenSSL.SSL.WantWriteError, err:
            wc.log.debug(wc.LOG_NET, '%s want write error', self)
            # you _are_ already writing, stupid
            return
        except OpenSSL.SSL.WantX509LookupError, err:
            wc.log.exception(wc.LOG_PROXY, "%s ssl write message", self)
            return
        except OpenSSL.SSL.ZeroReturnError, err:
            wc.log.debug(wc.LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except OpenSSL.SSL.Error, err:
            wc.log.exception(wc.LOG_PROXY, "write error")
            self.handle_error(str(err))
            return
        wc.log.debug(wc.LOG_NET, '%s => wrote %d', self, num_sent)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()
