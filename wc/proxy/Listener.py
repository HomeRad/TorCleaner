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
TCP socket listener.
"""

import socket
import wc
import wc.configuration
import wc.log
import wc.proxy.Dispatcher


class Listener (wc.proxy.Dispatcher.Dispatcher):
    """
    A listener accepts connections on a specified port. Each
    accepted incoming connection gets delegated to an instance of the
    handler class.
    """
    def __init__ (self, sockaddr, port, handler, sslctx=None):
        """
        Create a socket on specified port and start listening to it.
        """
        super(Listener, self).__init__()
        self.addr = (sockaddr, port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if sslctx is not None:
            import OpenSSL.SSL
            self.socket = OpenSSL.SSL.Connection(sslctx, self.socket)
            self.socket.set_accept_state()
        self.set_reuse_addr()
        self.bind(self.addr)
        # maximum number of queued connections
        self.listen(50)
        self.handler = handler
        if sockaddr:
            host = "%s:%d" % self.addr
        else:
            host = "*:%d" % port
        wc.log.info(wc.LOG_PROXY, "%s listening on %s tcp", wc.App, host)

    def __repr__ (self):
        """
        Return listener class and address.
        """
        return '<Listener:%s>' % str(self.addr)

    def log (self, msg):
        """
        Standard logging is disabled, we dont need it here.
        """
        pass

    def writable (self):
        """
        The listener is never writable, it returns None.
        """
        return None

    def handle_accept (self):
        """
        Start the handler class with the new socket.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s accept', self)
        args = self.accept()
        self.handler(*args)
