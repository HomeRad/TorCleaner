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
Server connections.
"""

import socket

from .. import log, LOG_PROXY, decorators
from . import CodingConnection


class Server(CodingConnection.CodingConnection):
    """
    Basic class for server connections.
    """

    def __init__(self, client, state):
        """
        Initialize server in given state, writing received data to client.
        """
        super(Server, self).__init__(state)
        self.client = client

    def client_abort(self):
        """
        The client has aborted the connection.
        """
        log.debug(LOG_PROXY, "%s Server.client_abort", self)
        self.client = None
        self.close()

    def try_connect(self):
        """
        Attempt connect to server given by self.addr. Close on error.
        """
        try:
            return self.connect(self.addr)
        except socket.error:
            # we never connected, but still the socket is in the socket map
            # so remove it
            self.del_channel()
            raise

    def handle_connect(self):
        """
        Make connection to remote server.
        """
        log.debug(LOG_PROXY, "%s Server.handle_connect", self)
        if self.state != 'connect':
            log.debug(LOG_PROXY, "%s client has closed", self)
            # the client has closed, and thus this server has too
            self.connected = False
            return
        self.process_connect()

    @decorators.notimplemented
    def process_connect(self):
        """
        Connect to remote server, must be implemented in subclass.
        """
        pass
