import sys
from wc.debug import *

class HttpProxyClient:
    """A class buffering all incoming data from a server for later use.
       Used to fetch javascript content in background.
       On completion the handler function is called.
       Buffered data is None on error, else the content string.
    """
    def __init__ (self, handler, args):
        self.handler = handler
        self.args = args
        self.connected = "True"


    def finish (self):
        if self.handler:
            self.handler(None, *self.args)
            self.handler = None


    def write (self, data):
        if self.handler:
            self.hander(data, *self.args)


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(NIGHTMARE, 'S/response', response)
        debug(NIGHTMARE, 'S/headers', headers)
        try:
            http_ver, status, msg = response.split()
            if status!="200":
                print >> sys.stderr, "error fetching data", status, msg
                self.finish()
        except:
            self.finish()


    def server_content (self, data):
        assert self.server
        debug(NIGHTMARE, 'S/content', self)
        self.write(data)


    def server_close (self):
        assert self.server
        debug(NIGHTMARE, 'S/close', self)
        self.finish()


    def server_abort (self):
        debug(NIGHTMARE, 'S/abort', self)
        self.finish()
