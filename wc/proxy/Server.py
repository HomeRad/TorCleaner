# -*- coding: iso-8859-1 -*-
"""server connections"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from StatefulConnection import StatefulConnection
from wc.log import *


class Server (StatefulConnection):
    """Basic class for server connections"""

    def __init__ (self, client, state):
        """initialize server in given state, writing received data to
           client"""
        super(Server, self).__init__(state)
        self.client = client


    def client_abort (self):
        """the client has aborted the connection"""
        debug(PROXY, "%s Server.client_abort", self)
        self.client = None
        self.close()


    def handle_connect (self):
        """make connection to remote server"""
        debug(PROXY, "%s Server.handle_connect", self)
        if self.state != 'connect':
            debug(PROXY, "%s client has closed", self)
            # the client has closed, and thus this server has too
            self.connected = False
            return
        self.process_connect()


    def process_connect (self):
        """connect to remote server, must be implemented in subclass"""
        raise NotImplementedError("must be implemented in a subclass")
