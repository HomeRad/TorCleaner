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
Stateful connections.
"""

from . import Connection


class StatefulConnection (Connection.Connection):
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

        @return: True iff no more read data can be processed
        @rtype: boolean
        """
        bytes_before = len(self.recv_buffer)
        state_before = self.state
        getattr(self, 'process_'+self.state)()
        bytes_after = len(self.recv_buffer)
        state_after = self.state
        return self.state == 'closed' or \
            (bytes_before == bytes_after and state_before == state_after)
