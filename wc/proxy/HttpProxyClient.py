# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.log import *
from wc.proxy.Headers import get_wc_client_headers
from wc.proxy import stripsite
from HttpServer import get_response_data
from ClientServerMatchmaker import ClientServerMatchmaker
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
        debug(PROXY, '%s init', str(self))


    def __repr__ (self):
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s %s>' % ('proxyclient', self.args[0], handler)


    def finish (self):
        debug(PROXY, '%s finish', str(self))
        if self.handler:
            self.handler(None, *self.args)
            self.handler = None


    def error (self, status, msg, txt=''):
        error(PROXY, '%s error %s %s %s', str(self), status, msg, txt)
        self.finish()


    def write (self, data):
        if self.handler:
            self.handler(data, *self.args)


    def server_response (self, server, response, status, headers):
        self.server = server
        assert self.server.connected
        debug(PROXY, '%s server_response %s', str(self), `response`)
        protocol, status, msg = get_response_data(response, self.args[0])
        if status in (302, 301):
            # eg: http://ezpolls.mycomputer.com/ezpoll.html?u=shuochen&p=1
            # make a new ClientServerMatchmaker
            url = self.server.headers.getheader("Location",
                         self.server.headers.getheader("Uri", ""))
            url = urlparse.urljoin(self.server.url, url)
            url = urllib.unquote(url)
            host = stripsite(url)[0]
            self.args = (url, self.args[1])
            # try again
            ClientServerMatchmaker(self,
                           "GET %s HTTP/1.1" % url, #request
                           get_wc_client_headers(host), #headers
                           '', #content
                           {'nofilter': None}, # nofilter
                           'identity', # compress
                           )
            return
        elif status!=200:
            error(PROXY, "%s got %s status %d %s",
                          str(self), protocol, status, `msg`)
            self.finish()


    def server_content (self, data):
        assert self.server
        debug(PROXY, '%s server_content with %d bytes', str(self), len(data))
        self.write(data)


    def server_close (self):
        assert self.server
        debug(PROXY, '%s server_close', str(self))
        self.finish()


    def server_abort (self):
        debug(PROXY, '%s server_abort', str(self))
        self.finish()


    def handle_local (self):
        error(PROXY, "%s handle_local %s", str(self), str(self.args))
        self.finish()
