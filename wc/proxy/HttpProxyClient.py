# -*- coding: iso-8859-1 -*-
"""internal http client"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import urlparse
from wc.log import *
from wc.url import stripsite, spliturl, url_norm, url_quote
from wc.proxy.Headers import get_wc_client_headers
from wc.proxy.HttpServer import get_response_data
from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
from wc.filter import FILTER_REQUEST
from wc.filter import FILTER_REQUEST_DECODE
from wc.filter import FILTER_REQUEST_MODIFY
from wc.filter import FILTER_REQUEST_ENCODE
from wc.filter import applyfilter, get_filterattrs, FilterRating


class HttpProxyClient (object):
    """A class buffering all incoming data from a server for later use.
       Used to fetch javascript content in background.
       On completion the handler function is called.
       Buffered data is None on error, else the content string.
    """

    def __init__ (self, handler, args):
        """args is a tuple (url, JS version)"""
        assert callable(handler)
        self.handler = handler
        self.args = args
        self.method = "GET"
        self.url = url_norm(self.args[0])
        self.scheme, self.hostname, self.port, self.document = spliturl(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        self.connected = True
        self.addr = ('localhost', 80)
        self.isredirect = False
        attrs = get_filterattrs(self.url, [FILTER_REQUEST])
        attrs['mime'] = 'application/x-javascript'
        request = "GET %s HTTP/1.0" % url_quote(self.url)
        request = applyfilter(FILTER_REQUEST_DECODE, request, "filter", attrs)
        request = applyfilter(FILTER_REQUEST_MODIFY, request, "filter", attrs)
        self.request = applyfilter(FILTER_REQUEST_ENCODE, request, "filter", attrs)
        debug(PROXY, '%s init', self)


    def __repr__ (self):
        """object representation"""
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s %s>' % ('proxyclient', self.args[0], handler)


    def finish (self):
        """tell handler all data is written and remove handler"""
        debug(PROXY, '%s finish', self)
        if self.handler:
            self.handler(None, *self.args)
            self.handler = None


    def error (self, status, msg, txt=''):
        """on error the client finishes"""
        error(PROXY, '%s error %s %s %s', self, status, msg, txt)
        self.finish()


    def write (self, data):
        """give data to handler"""
        if self.handler:
            self.handler(data, *self.args)


    def server_response (self, server, response, status, headers):
        """Follow redirects, and finish on errors. For HTTP status 2xx
           continue."""
        self.server = server
        assert self.server.connected
        debug(PROXY, '%s server_response %r', self, response)
        protocol, status, msg = get_response_data(response, self.args[0])
        debug(PROXY, '%s response %s %d %s', self, protocol, status, msg)
        if status in (302, 301):
            self.isredirect = True
        elif not (200 <= status < 300):
            error(PROXY, "%s got %s status %d %r", self, protocol, status, msg)
            self.finish()


    def server_content (self, data):
        """delegate server content to handler if it is not from a redirect
           response"""
        assert self.server
        debug(PROXY, '%s server_content with %d bytes', self, len(data))
        if data and not self.isredirect:
            self.write(data)


    def server_close (self, server):
        """The server has closed. Either redirect to new url, or finish"""
        assert self.server
        debug(PROXY, '%s server_close', self)
        if self.isredirect:
            self.redirect()
        else:
            self.finish()


    def server_abort (self):
        """The server aborted, so finish"""
        debug(PROXY, '%s server_abort', self)
        self.finish()


    def handle_local (self):
        """Local data is not allowed here, finish."""
        error(PROXY, "%s handle_local %s", self, self.args)
        self.finish()


    def redirect (self):
        """handle redirection to new url"""
        assert self.server
        # eg: http://ezpolls.mycomputer.com/ezpoll.html?u=shuochen&p=1
        # make a new ClientServerMatchmaker
        url = self.server.headers.getheader("Location",
                     self.server.headers.getheader("Uri", ""))
        url = urlparse.urljoin(self.server.url, url)
        self.url = url_norm(url)
        self.args = (self.url, self.args[1])
        self.isredirect = False
        debug(PROXY, "%s redirected", self)
        self.scheme, self.hostname, self.port, self.document = spliturl(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        host = stripsite(self.url)[0]
        mime = self.server.mime
        content = ''
        # note: use HTTP/1.0 for JavaScript
        request = "GET %s HTTP/1.0"%url_quote(self.url)
        # close the server and try again
        self.server = None
        headers = get_wc_client_headers(host)
        headers['Accept-Encoding'] = 'identity\r'
        ClientServerMatchmaker(self, request, headers, content, mime=mime)
