# -*- coding: iso-8859-1 -*-
"""
Server connections.
"""

import socket
import errno

import wc
import wc.log
import wc.proxy.StatefulConnection


class Server (wc.proxy.StatefulConnection.StatefulConnection):
    """
    Basic class for server connections.
    """

    def __init__ (self, client, state):
        """
        Initialize server in given state, writing received data to client.
        """
        super(Server, self).__init__(state)
        self.client = client

    def client_abort (self):
        """
        The client has aborted the connection.
        """
        wc.log.debug(wc.LOG_PROXY, "%s Server.client_abort", self)
        self.client = None
        self.close()

    def try_connect (self):
        """
        Attempt connect to server given by self.addr. Close on error.
        """
        try:
            return self.connect(self.addr)
        except (socket.timeout, socket.error):
            # we never connected, but still the socket is in the socket map
            # so remove it
            self.del_channel()
            raise

    def handle_connect (self):
        """
        Make connection to remote server.
        """
        wc.log.debug(wc.LOG_PROXY, "%s Server.handle_connect", self)
        if self.state != 'connect':
            wc.log.debug(wc.LOG_PROXY, "%s client has closed", self)
            # the client has closed, and thus this server has too
            self.connected = False
            return
        self.process_connect()

    def process_connect (self):
        """
        Connect to remote server, must be implemented in subclass.
        """
        raise NotImplementedError("must be implemented in a subclass")

