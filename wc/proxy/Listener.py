import asyncore, socket
from wc import config
from wc.log import *

class Listener (asyncore.dispatcher):
    """A listener accepts connections on a specified port. Each
       accepted incoming connection gets delegated to an instance of the
       handler class"""
    def __init__ (self, port, handler):
        """create a socket on specified port and start listening to it"""
        asyncore.dispatcher.__init__(self)
        self.addr = (('', 'localhost')[config['local_sockets_only']], port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # disable NAGLE algorithm, which means sending pending data
        # immediately, possibly wasting bandwidth
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.set_reuse_addr()
        self.bind(self.addr)
        # 5 is the maximum number of queued connections
        self.listen(5)
        self.handler = handler

    def __repr__ (self):
        return '<Listener:%s>' % self.addr[1]

    def log (self, msg):
        """standard logging is disabled, we dont need it here"""
        pass

    def writable (self):
        """The listener is never writable, it returns None"""
        return None

    def handle_accept (self):
        """start the handler class with the new socket"""
        debug(PROXY, 'Proxy: accept %s', str(self))
        apply(self.handler, self.accept())

    def handle_error (self, what):
        exception(PROXY, what)
