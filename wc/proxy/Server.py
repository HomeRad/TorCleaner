# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from StatefulConnection import StatefulConnection
from wc.log import *


class Server (StatefulConnection):
    def __init__ (self, client, state):
        super(Server, self).__init__(state)
        self.client = client


    def client_abort (self):
        debug(PROXY, "%s Server.client_abort", self)
        self.client = None
        self.close()


    def handle_connect (self):
        debug(PROXY, "%s Server.handle_connect", self)
        if self.state != 'connect':
            debug(PROXY, "%s client has closed", self)
            # the client has closed, and thus this server has too
            self.connected = False
            return
        self.process_connect()


    def writable (self):
        """a server is writable if we're connecting"""
        return self.send_buffer or self.state=='connect'


    def readable (self):
        """a server is readable if we're connected and in a readable state"""
        return self.connected and self.state!='closed'


    def process_connect (self):
        raise NotImplementedError("must be implemented in a subclass")
