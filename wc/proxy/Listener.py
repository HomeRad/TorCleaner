import asyncore, socket, sys
from wc import debug,config
from wc.debug_levels import *

class Listener (asyncore.dispatcher):
    def __init__ (self, port, handler):
        asyncore.dispatcher.__init__(self)
        self.addr = (('', 'localhost')[config['local_sockets_only']], port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.addr)
        self.listen(5)
        self.handler = handler

    def __repr__ (self):
        return '<Listener:%s>' % self.addr[1]

    def log (self, msg):
        pass

    def writable (self):
        return False

    def handle_accept (self):
        #debug(HURT_ME_PLENTY, 'accept', self)
        apply(self.handler, self.accept())

    def handle_error (self, what, type, value, tb=None):
        print >> sys.stderr, what, self, type, value
        if tb:
            import traceback
            traceback.print_tb(tb)
