import asyncore,socket
from wc import debug
from wc.debug_levels import *

local_sockets_only = 1

class Listener(asyncore.dispatcher):
    def __init__(self, port, handler):
        asyncore.dispatcher.__init__(self)
        self.addr = (('', 'localhost')[local_sockets_only], port)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.addr)
        self.listen(5)
        self.handler = handler

    def __repr__(self):
        return '<Listener:%s>' % self.addr[1]
    
    def log(self, msg):
        pass

    def writable(self):
        return 0
    
    def handle_accept(self):
        debug(HURT_ME_PLENTY, 'accept', self)
        apply(self.handler, self.accept())

    def handle_error(self, type, value, tb=None):
        debug(ALWAYS, 'error', self, type, value)
	import traceback
        if tb: traceback.print_tb(tb)
