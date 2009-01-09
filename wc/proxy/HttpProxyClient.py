# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Internal http client.
"""
import urlparse
from . import Headers, ClientServerMatchmaker
from .decoder import UnchunkStream
from .. import log, LOG_PROXY, filter as webfilter, url as urlutil
from ..http import parse_http_response
from ..http.header import WcMessage

def funcname (func):
    name = func.func_name
    if hasattr(func, 'im_class'):
        name = func.im_class.__name__+"."+name
    return name


class HttpProxyClient (object):
    """
    A class buffering all incoming data from a server for later use.
    Used to fetch javascript content in background.
    On completion the handler function is called.
    Buffered data is None on error, else the content string.
    """

    def __init__ (self, localhost, url, method="GET"):
        """
        Args is a tuple (url, JS version).
        """
        self.handlers = {}
        self.method = method
        self.decoders = []
        self.url = urlutil.url_norm(url)[0]
        self.scheme, self.hostname, self.port, self.document = \
                                                  urlutil.url_split(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        self.connected = True
        self.addr = ('#wc_proxy_client#', 80)
        self.localhost = localhost
        self.isredirect = False
        self.headers = WcMessage()
        attrs = webfilter.get_filterattrs(self.url, self.localhost,
                                          [webfilter.STAGE_REQUEST])
        # note: use HTTP/1.0 for older browsers
        request = "%s %s HTTP/1.0" % (self.method, self.url)
        for stage in webfilter.ClientFilterStages:
            request = webfilter.applyfilter(stage, request, "filter", attrs)
        self.request = request
        log.debug(LOG_PROXY, '%s init', self)

    def add_content_handler (self, handler, args=()):
        self.handlers['content'] = (handler, args)
        assert self.method != "HEAD", "No content for HEAD method"

    def add_header_handler (self, handler, args=()):
        self.handlers['headers'] = (handler, args)

    def __repr__ (self):
        """
        Object representation.
        """
        slist = []
        for key, value in self.handlers.items():
            handler, args = value
            s = "%s: %s" % (key, funcname(handler))
            if args:
                s += " %s" % args[0]
            slist.append(s)
        return '<%s: %s>' % ('proxyclient', "\n ".join(slist))

    def flush_coders (self, coders, data=""):
        while coders:
            log.debug(LOG_PROXY, "flush %s", coders[0])
            data = coders[0].process(data)
            data += coders[0].flush()
            del coders[0]
        return data

    def finish (self):
        """
        Tell handler all data is written and remove handler.
        """
        log.debug(LOG_PROXY, '%s finish', self)
        data = self.flush_coders(self.decoders)
        if "content" in self.handlers:
            handler, args = self.handlers['content']
            if data:
                handler(data, *args)
            handler(None, *args)
            del self.handlers["content"]

    def error (self, status, msg, txt=''):
        """
        On error the client finishes.
        """
        log.warn(LOG_PROXY, '%s error %s %s %s', self, status, msg, txt)
        self.finish()

    def write (self, data):
        """
        Give data to handler.
        """
        for decoder in self.decoders:
            data = decoder.process(data)
        if "content" in self.handlers and data:
            handler, args = self.handlers['content']
            handler(data, *args)

    def server_response (self, server, response, status, headers):
        """
        Follow redirects, and finish on errors. For HTTP status 2xx continue.
        """
        self.server = server
        assert self.server.connected
        log.debug(LOG_PROXY, '%s server_response %r', self, response)
        version, status, msg = parse_http_response(response, self.url)
        # XXX check version
        log.debug(LOG_PROXY, '%s response %s %d %s',
            self, version, status, msg)
        if status in (302, 301):
            self.isredirect = True
        else:
            if "headers" in self.handlers:
                handler, args = self.handlers['headers']
                handler(headers, *args)
                del self.handlers["headers"]
            if not (200 <= status < 300):
                log.debug(LOG_PROXY,
                    "%s got %s status %d %r", self, version, status, msg)
                self.finish()
        if headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            log.debug(LOG_PROXY,
                '%s Transfer-encoding %r', self, headers['Transfer-encoding'])
            unchunker = UnchunkStream.UnchunkStream(self)
            self.decoders.append(unchunker)

    def write_trailer (self, data):
        pass

    def server_content (self, data):
        """
        Delegate server content to handler if it is not from a redirect
        response.
        """
        assert self.server
        log.debug(LOG_PROXY,
            '%s server_content with %d bytes', self, len(data))
        if data and not self.isredirect:
            self.write(data)

    def server_close (self, server):
        """
        The server has closed. Either redirect to new url, or finish.
        """
        assert self.server
        log.debug(LOG_PROXY, '%s server_close', self)
        if self.isredirect:
            self.redirect()
        else:
            self.finish()

    def server_abort (self):
        """
        The server aborted, so finish.
        """
        log.debug(LOG_PROXY, '%s server_abort', self)
        self.finish()

    def handle_local (self):
        """
        Local data is not allowed here, finish.
        """
        log.error(LOG_PROXY, "%s handle_local %s", self)
        self.finish()

    def redirect (self):
        """
        Handle redirection to new url.
        """
        assert self.server
        # eg: http://ezpolls.mycomputer.com/ezpoll.html?u=shuochen&p=1
        # make a new ClientServerMatchmaker
        url = self.server.headers.getheader("Location",
                     self.server.headers.getheader("Uri", ""))
        url = urlparse.urljoin(self.server.url, url)
        self.url = urlutil.url_norm(url)[0]
        self.isredirect = False
        log.debug(LOG_PROXY, "%s redirected", self)
        self.scheme, self.hostname, self.port, self.document = \
                                                  urlutil.url_split(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        host = urlutil.stripsite(self.url)[0]
        mime_types = self.server.mime_types
        content = ''
        attrs = webfilter.get_filterattrs(self.url, self.localhost,
                                          [webfilter.STAGE_REQUEST])
        # note: use HTTP/1.0 for older browsers
        request = "%s %s HTTP/1.0" % (self.method, self.url)
        for stage in webfilter.ClientFilterStages:
            request = webfilter.applyfilter(stage, request, "filter", attrs)
        if self.request == request:
            # avoid request loop
            self.finish()
            return
        # close the server and try again
        self.server = None
        headers = Headers.get_wc_client_headers(host)
        headers['Accept-Encoding'] = 'identity\r'
        ClientServerMatchmaker.ClientServerMatchmaker(
                    self, request, headers, content, mime_types=mime_types)
