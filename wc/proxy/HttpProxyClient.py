import sys
from wc.debug import *

class HttpProxyClient:
    """A class buffering all incoming data from a server for later use.
       Used to fetch javascript content in background.
       On completion the handler function is called.
       Buffered data is None on error, else the content string.
    """
    def __init__ (self, handler, args):
        assert callable(handler)
        self.handler = handler
        self.args = args
        self.connected = "True"
        self.addr = ('localhost', 80)
        debug(NIGHTMARE, 'Proxy: CP/init', self)


    def __repr__ (self):
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s>' % ('proxyclient', handler)


    def finish (self):
        debug(NIGHTMARE, 'Proxy: CP/finish', self)
        if self.handler:
            self.handler(None, *self.args)
            self.handler = None


    def error (self, status, msg, txt=''):
        pass


    def write (self, data):
        if self.handler:
            self.handler(data, *self.args)


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(NIGHTMARE, 'Proxy: CP/Server response', self, `response`)
        try:
            http_ver, status, msg = response.split()
            if status!="200":
                print >> sys.stderr, "error fetching data", status, msg
                self.finish()
        except:
            self.finish()


    def server_content (self, data):
        assert self.server
        debug(NIGHTMARE, 'Proxy: CP/Server content', self)
        self.write(data)


    def server_close (self):
        assert self.server
        debug(NIGHTMARE, 'Proxy: CP/Server close', self)
        self.finish()


    def server_abort (self):
        debug(NIGHTMARE, 'Proxy: CP/server_abort', self)
        self.finish()
