# -*- coding: iso-8859-1 -*-
"""
Stateful connections.
"""

import wc.proxy.Connection


class StatefulConnection (wc.proxy.Connection.Connection):
    """
    Connection class allowing the connection to be in a specified state.
    """

    def __init__ (self, state, sock=None):
        """
        Initialize connection with given start state.
        """
        self.state = state
        super(StatefulConnection, self).__init__(sock=sock)

    def readable (self):
        """
        A connection is readable if we're connected and not in a close state.
        """
        return self.connected and self.state not in ('closed', 'unreadable')

    def delegate_read (self):
        """
        Delegate a read process to process_* funcs according to the current
        state.
        """
        bytes_before = len(self.recv_buffer)
        state_before = self.state
        getattr(self, 'process_'+self.state)()
        bytes_after = len(self.recv_buffer)
        state_after = self.state
        return self.state == 'closed' or \
           (bytes_before == bytes_after and state_before == state_after)
