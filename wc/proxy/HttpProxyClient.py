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
        debug(NIGHTMARE, 'ProxyClient: init', self)


    def __repr__ (self):
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s>' % ('proxyclient', handler)


    def finish (self):
        debug(NIGHTMARE, 'ProxyClient: finish', self)
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
        debug(NIGHTMARE, 'ProxyClient: server_response', self, `response`)
        try:
            http_ver, status, msg = response.split()
            if status in ["302", "301"]:
                # eg: http://ezpolls.mycomputer.com/ezpoll.html?u=shuochen&p=1
                # make a new ClientServerMatchmaker
                url = self.server.headers.getheader("Location",
                             self.server.headers.getheader("Uri", ""))
                url = urlparse.urljoin(self.server.url, url)
                url = unquote(url)
                self.args = (url, args[1])
                # try again
                return ClientServerMatchmaker(self,
                               "GET %s HTTP/1.1" % url, #request
                               {}, #headers
                               '', #content
                               {'nofilter': None}, # nofilter
                               'identity', # compress
                               )
            elif status!="200":
                print >> sys.stderr, "Error fetching data", status, msg
                self.finish()
        except:
            self.finish()


    def server_content (self, data):
        assert self.server
        debug(NIGHTMARE, 'ProxyClient: server_content', self)
        self.write(data)


    def server_close (self):
        assert self.server
        debug(NIGHTMARE, 'ProxyClient: server_close', self)
        self.finish()


    def server_abort (self):
        debug(NIGHTMARE, 'ProxyClient: server_abort', self)
        self.finish()
