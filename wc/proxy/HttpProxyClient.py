# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.log import *
import urlparse, urllib

class HttpProxyClient (object):
    """A class buffering all incoming data from a server for later use.
       Used to fetch javascript content in background.
       On completion the handler function is called.
       Buffered data is None on error, else the content string.
    """
    def __init__ (self, handler, args):
        assert callable(handler)
        self.handler = handler
        self.args = args
        self.connected = True
        self.addr = ('localhost', 80)
        debug(PROXY, 'ProxyClient: init %s', str(self))


    def __repr__ (self):
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s>' % ('proxyclient', handler)


    def finish (self):
        debug(PROXY, 'ProxyClient: finish %s', str(self))
        if self.handler:
            self.handler(None, *self.args)
            self.handler = None


    def error (self, status, msg, txt=''):
        self.finish()


    def write (self, data):
        if self.handler:
            self.handler(data, *self.args)


    def server_response (self, server, response, headers):
        self.server = server
        assert self.server.connected
        debug(PROXY, 'ProxyClient: server_response %s %s', str(self), `response`)
        try:
            http_ver, status, msg = response.split()
            if status in ["302", "301"]:
                # eg: http://ezpolls.mycomputer.com/ezpoll.html?u=shuochen&p=1
                # make a new ClientServerMatchmaker
                url = self.server.headers.getheader("Location",
                             self.server.headers.getheader("Uri", ""))
                url = urlparse.urljoin(self.server.url, url)
                url = urllib.unquote(url)
                self.args = (url, self.args[1])
                # try again
                ClientServerMatchmaker(self,
                               "GET %s HTTP/1.1" % url, #request
                               {}, #headers
                               '', #content
                               {'nofilter': None}, # nofilter
                               'identity', # compress
                               )
                return
            elif status!="200":
                error(PROXY, "fetching data status: %s %s", status, msg)
                self.finish()
        except:
            # XXX really catch all exceptions?
            self.finish()


    def server_content (self, data):
        assert self.server
        debug(PROXY, 'ProxyClient: server_content %s', str(self))
        self.write(data)


    def server_close (self):
        assert self.server
        debug(PROXY, 'ProxyClient: server_close %s', str(self))
        self.finish()


    def server_abort (self):
        debug(PROXY, 'ProxyClient: server_abort %s', str(self))
        self.finish()


    def handle_local (self):
        error(PROXY, "ProxyClient handle_local %s", str(self.args))
        self.finish()
