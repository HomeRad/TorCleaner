from Connection import Connection

# XXX there should be an API for this class, and it should be moved
# elsewhere
class Server (Connection):
    def __init__ (self, client):
        Connection.__init__(self)
        self.client = client


    def client_abort (self):
        self.client = None
        if self.connected:
            self.close()


    def handle_connect (self):
        if self.state != 'connect':
            # the client has closed, and thus this server has too
            self.connected = 0
            return
        self.process_connect()
