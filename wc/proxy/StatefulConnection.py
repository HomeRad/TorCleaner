# -*- coding: iso-8859-1 -*-
"""stateful connections"""

import wc.proxy.Connection


class StatefulConnection (wc.proxy.Connection.Connection):
    """connection class allowing the connection to be in a specified state
    """

    def __init__ (self, state, sock=None):
        """initialize connection with given start state"""
        self.state = state
        super(StatefulConnection, self).__init__(sock=sock)

    def readable (self):
        """a connection is readable if we're connected and not in a
           close state
        """
        return self.connected and self.state not in ('closed', 'unreadable')

    def writable (self):
        """a connection is writable if we're connecting or if data is
           available
        """
        return self.send_buffer or self.state == 'connect'

    def delegate_read (self):
        """delegate a read process to process_* funcs according to the
           current state
        """
        bytes_before = len(self.recv_buffer)
        state_before = self.state
        getattr(self, 'process_'+self.state)()
        bytes_after = len(self.recv_buffer)
        state_after = self.state
        return self.state == 'closed' or \
           (bytes_before == bytes_after and state_before == state_after)
