from Connection import Connection
from wc.log import *

# XXX there should be an API for this class, and it should be moved
# elsewhere
class Server (Connection):
    def __init__ (self, client):
        Connection.__init__(self)
        self.client = client


    def client_abort (self):
        debug(PROXY, "class Server: client_abort")
        self.client = None
        if self.connected:
            self.close()


    def handle_connect (self):
        debug(PROXY, "class Server: handle_connect")
        if self.state != 'connect':
            # the client has closed, and thus this server has too
            self.connected = 0
            return
        self.process_connect()
