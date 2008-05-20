# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2008 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
SSL connection, usable for both client and server connections.
"""

from .. import log, LOG_PROXY, LOG_NET
from . import Connection
from OpenSSL import SSL


class SslConnection (Connection.Connection):
    """
    Mix-in class for SSL connections.
    """

    def handle_read (self):
        """
        Read data from SSL connection, put it into recv_buffer and call
        process_read.
        """
        assert self.connected
        log.debug(LOG_PROXY,
            '%s SslConnection.handle_read', self)
        if len(self.recv_buffer) > Connection.MAX_BUFSIZE:
            self.handle_error('read buffer full')
            return
        try:
            data = self.socket.read(self.socket_rcvbuf)
            log.debug(LOG_NET, 'have read data %r', data)
        except SSL.WantReadError, err:
            log.debug(LOG_NET, '%s want read error', self)
            # you _are_ already reading, stupid
            return
        except SSL.WantWriteError, err:
            log.debug(LOG_NET, '%s want write error', self)
            # you want to write? here you go
            self.handle_write()
            return
        except SSL.WantX509LookupError, err:
            log.exception(LOG_PROXY, "%s ssl read message", self)
            return
        except SSL.ZeroReturnError, err:
            log.debug(LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except SSL.Error, err:
            log.exception(LOG_PROXY, "%s read error", self)
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            log.debug(LOG_PROXY, "%s closed, got empty data", self)
            return
        log.debug(LOG_NET, '%s <= read %d', self, len(data))
        self.recv_buffer += data
        self.process_read()

    def handle_write (self):
        """
        Write data from send_buffer to connection socket.
        Execute a possible pending close.
        """
        assert self.connected
        assert self.send_buffer
        log.debug(LOG_PROXY, '%s SslConnection.handle_write', self)
        num_sent = 0
        data = self.send_buffer[:self.socket_sndbuf]
        log.debug(LOG_NET, 'have written data %r', data)
        try:
            num_sent = self.socket.write(data)
        except SSL.WantReadError, err:
            log.debug(LOG_NET, '%s want read error', self)
            # you want to read? here you go
            self.handle_read()
            return
        except SSL.WantWriteError, err:
            log.debug(LOG_NET, '%s want write error', self)
            # you _are_ already writing, stupid
            return
        except SSL.WantX509LookupError, err:
            log.exception(LOG_PROXY, "%s ssl write message", self)
            return
        except SSL.ZeroReturnError, err:
            log.debug(LOG_PROXY, "%s ssl finished successfully", self)
            self.delayed_close()
            return
        except SSL.Error, err:
            log.exception(LOG_PROXY, "write error")
            self.handle_error(str(err))
            return
        log.debug(LOG_NET, '%s => wrote %d', self, num_sent)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()
