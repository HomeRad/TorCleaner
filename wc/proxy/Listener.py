# -*- coding: iso-8859-1 -*-
"""TCP socket listener"""

import socket
import wc
import wc.log
import wc.proxy.Dispatcher


class Listener (wc.proxy.Dispatcher.Dispatcher):
    """A listener accepts connections on a specified port. Each
       accepted incoming connection gets delegated to an instance of the
       handler class"""
    def __init__ (self, port, handler, sslctx=None):
        """create a socket on specified port and start listening to it"""
        super(Listener, self).__init__()
        self.addr = (('', 'localhost')[wc.config['local_sockets_only']], port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=sslctx)
        if sslctx is not None:
            self.socket.set_accept_state()
        self.set_reuse_addr()
        self.bind(self.addr)
        # maximum number of queued connections
        self.listen(50)
        self.handler = handler

    def __repr__ (self):
        """return listener class and address"""
        return '<Listener:%s>' % self.addr[1]

    def log (self, msg):
        """standard logging is disabled, we dont need it here"""
        pass

    def writable (self):
        """The listener is never writable, it returns None"""
        return None

    def handle_accept (self):
        """start the handler class with the new socket"""
        wc.log.debug(wc.LOG_PROXY, '%s accept', self)
        args = self.accept()
        self.handler(*args)

