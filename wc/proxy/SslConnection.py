# -*- coding: iso-8859-1 -*-
"""ssl connection, usable for both client and server connections"""

import wc
import wc.proxy.Connection
from OpenSSL import SSL
import wc.log


class SslConnection (wc.proxy.Connection.Connection):
    """mix-in class for SSL connections"""
    def handle_read (self):
        """read data from SSL connection, put it into recv_buffer and call
           process_read"""
        assert self.connected
        wc.log.debug(wc.LOG_PROXY, '%s SslConnection.handle_read', self)
        if len(self.recv_buffer) > wc.proxy.Connection.MAX_BUFSIZE:
            wc.log.warn(wc.LOG_PROXY, '%s read buffer full', self)
            return
        try:
            data = self.socket.read(wc.proxy.Connection.RECV_BUFSIZE)
        except SSL.WantReadError:
            # you _are_ already reading, stupid
            return
        except SSL.WantWriteError:
            # you want to write? here you go
            self.handle_write()
            return
        except SSL.WantX509LookupError, err:
            wc.log.exception(wc.LOG_PROXY, "%s ssl read message", self)
            return
        except SSL.ZeroReturnError, err:
            wc.log.debug(wc.LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except SSL.Error, err:
            wc.log.exception(wc.LOG_PROXY, "read error %s", err)
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            wc.log.debug(wc.LOG_PROXY, "%s closed, got empty data", self)
            return
        wc.log.debug(wc.LOG_CONNECTION, '%s <= read %d', self, len(data))
        wc.log.debug(wc.LOG_CONNECTION, 'data %r', data)
        self.recv_buffer += data
        self.process_read()


    def handle_write (self):
        """Write data from send_buffer to connection socket.
           Execute a possible pending close."""
        assert self.connected
        assert self.send_buffer
        wc.log.debug(wc.LOG_PROXY, '%s SslConnection.handle_write', self)
        num_sent = 0
        data = self.send_buffer[:wc.proxy.Connection.SEND_BUFSIZE]
        try:
            num_sent = self.socket.write(data)
        except SSL.WantReadError:
            # you want to read? here you go
            self.handle_read()
            return
        except SSL.WantWriteError:
            # you _are_ already writing, stupid
            return
        except SSL.WantX509LookupError, err:
            wc.log.exception(wc.LOG_PROXY, "%s ssl write message", self)
            return
        except SSL.ZeroReturnError, err:
            wc.log.debug(wc.LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except SSL.Error, err:
            wc.log.exception(wc.LOG_PROXY, "write error %s", err)
            self.handle_error(str(err))
            return
        wc.log.debug(wc.LOG_CONNECTION, '%s => wrote %d', self, num_sent)
        wc.log.debug(wc.LOG_CONNECTION, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()
