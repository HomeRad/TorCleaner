# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from Connection import Connection


class StatefulConnection (Connection):
    def __init__ (self, state, sock=None):
        super(StatefulConnection, self).__init__(sock=sock)
        self.state = state


    def writable (self):
        """a connection is writable if we're connecting"""
        return self.send_buffer or self.state=='connect'


    def readable (self):
        """a connection is readable if we're connected and not in a close state"""
        return self.connected and self.state!='closed'
