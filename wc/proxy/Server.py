# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from Connection import Connection
from wc.log import *

# XXX there should be an API for this class, and it should be moved
# elsewhere
class Server (Connection):
    def __init__ (self, client, state):
        super(Server, self).__init__()
        self.client = client
        self.state = state


    def client_abort (self):
        debug(PROXY, "class Server: client_abort")
        self.client = None
        if self.connected:
            self.close()


    def handle_connect (self):
        debug(PROXY, "class Server: handle_connect")
        if self.state != 'connect':
            # the client has closed, and thus this server has too
            self.connected = False
            return
        self.process_connect()


    def process_connect (self):
        raise NotImplementedError("must be implemented in a subclass")
