# -*- coding: iso-8859-1 -*-
# Copyright (c) 2000, Amit Patel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of Amit Patel nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Connection handling.
"""

# asyncore problem -- we can't separately register for reading/writing
# (less efficient: it calls writable(), readable() a LOT)
# (however, for the proxy it may not be a big deal)

import socket
import errno
import os

import wc
import wc.decorators
import wc.log
import wc.proxy.Dispatcher

# to prevent DoS attacks, specify a maximum buffer size of 10MB
MAX_BUFSIZE = 10*1024*1024


class Connection (wc.proxy.Dispatcher.Dispatcher):
    """
    Add buffered input and output capabilities.
    """

    def __init__ (self, sock=None):
        """
        Initialize buffers.
        """
        super(Connection, self).__init__(sock=sock)
        self.reset()
        # reuse counter for persistent connections
        self.sequence_number = 0

    def reset (self):
        """
        Reset send and receive buffers.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s buffer reset', self)
        self.recv_buffer = ''
        self.send_buffer = ''
        # True if data has still to be written before closing
        self.close_pending = False
        # True if connection should not be closed
        self.persistent = False

    def readable (self):
        """
        Return True if connection is readable.
        """
        return self.connected

    def read (self, bytes=None):
        """
        Read up to LEN bytes from the internal buffer.
        """
        if bytes is None:
            bytes = self.socket_rcvbuf
        data = self.recv_buffer[:bytes]
        self.recv_buffer = self.recv_buffer[bytes:]
        return data

    def handle_read (self):
        """
        Read data from connection, put it into recv_buffer and call
        process_read.
        """
        assert self.connected
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.handle_read', self)
        if len(self.recv_buffer) > MAX_BUFSIZE:
            self.handle_error('read buffer full')
            return
        try:
            data = self.recv(self.socket_rcvbuf)
        except socket.error, err:
            if err == errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            assert wc.log.debug(wc.LOG_PROXY,
                                "%s closed, got empty data", self)
            self.persistent = False
            return
        assert wc.log.debug(wc.LOG_NET, '%s <= read %d', self, len(data))
        assert wc.log.debug(wc.LOG_NET, 'data %r', data)
        self.recv_buffer += data
        self.process_read()

    @wc.decorators.notimplemented
    def process_read (self):
        """
        Handle read event.
        """
        pass

    def writable (self):
        """
        Return True if connection is writable.
        """
        return self.connected and self.send_buffer

    def write (self, data):
        """
        Write data to the internal buffer.
        """
        self.send_buffer += data

    def handle_write (self):
        """
        Write data from send_buffer to connection socket.
        Execute a possible pending close.
        """
        assert self.connected
        assert self.send_buffer
        assert wc.log.debug(wc.LOG_PROXY, '%s handle_write', self)
        num_sent = 0
        data = self.send_buffer[:self.socket_sndbuf]
        try:
            num_sent = self.send(data)
        except socket.error, err:
            if err == errno.EAGAIN:
                # try again later
                return
            self.handle_error(str(err))
            return
        assert wc.log.debug(wc.LOG_NET, '%s => wrote %d', self, num_sent)
        assert wc.log.debug(wc.LOG_NET, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()

    def handle_connect (self):
        """
        Empty function; per default we don't connect to anywhere.
        """
        pass

    def close (self):
        """
        Close connection.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.close', self)
        self.close_pending = False
        if self.persistent:
            self.close_reuse()
        else:
            self.close_close()

    def close_close (self):
        """
        Close the connection socket.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.close_close', self)
        if self.connected:
            self.connected = False
        super(Connection, self).close()

    def handle_close (self):
        """
        If we are still connected, wait until all data is sent, then close.
        Otherwise just close.
        """
        assert wc.log.debug(wc.LOG_PROXY, "%s Connection.handle_close", self)
        if self.connected:
            self.delayed_close()
        else:
            self.close()

    def close_ready (self):
        """
        Return True if all data is sent and this connection can be closed.
        """
        return not self.send_buffer

    def delayed_close (self):
        """
        Close whenever the data has been sent.
        """
        assert self.connected
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.delayed_close', self)
        if not self.close_ready():
            # Do not close yet because there is still data to send
            assert wc.log.debug(wc.LOG_PROXY, '%s close ready channel', self)
            self.close_pending = True
        else:
            self.close()

    def close_reuse (self):
        """
        Don't close the socket, just reset the connection state.
        Must only be called for persistent connections.
        """
        assert self.persistent
        assert self.connected
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.close_reuse %d',
                     self, self.sequence_number)
        self.sequence_number += 1

    def handle_error (self, what):
        """
        Print error and close the connection.
        """
        assert wc.log.debug(wc.LOG_PROXY, "%s error %s", self, what)
        super(Connection, self).handle_error(what)
        self.close()

    def handle_expt (self):
        """
        Handle socket exception.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s Connection.handle_expt', self)
        try:
            # Get the socket error and report it. Note that SO_ERROR
            # clears the error.
            err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            wc.log.warn(wc.LOG_PROXY,
                    "%s socket exception error %s", self, os.strerror(err))
        except socket.error:
            wc.log.exception(wc.LOG_PROXY,
                             "%s could not get socket exception error", self)
        if not self.connected:
            # The non-blocking socket connect() had an error. This is
            # a Windows peculiarity, on Unix a failed connect() puts
            # the socket in the read list, and issues an empty read.
            self.handle_error("socket exception while connecting")
            return
        # Try to read out-of-band data (which might not yet
        # have arrived, despite the exception condition).
        if len(self.recv_buffer) > MAX_BUFSIZE:
            self.handle_error('read buffer full')
            return
        try:
            data = self.recv(self.socket_rcvbuf, flags=socket.MSG_OOB)
        except socket.error, err:
            if err == errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        if not data:
            # Out-of-band data might just not have been arrived, even
            # if the error condition is set.
            assert wc.log.debug(wc.LOG_PROXY,
                                "%s got empty out-of-band data", self)
            return
        assert wc.log.debug(wc.LOG_NET, '%s <= read %d', self, len(data))
        assert wc.log.debug(wc.LOG_NET, 'data %r', data)
        self.recv_buffer += data
