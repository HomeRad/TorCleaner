# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
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
import wc.http
import wc.proxy.Headers
import wc.proxy.HttpServer
import wc.proxy.HttpClient
import wc.proxy.ClientServerMatchmaker
import wc.proxy.decoder.UnchunkStream
import wc.filter
import wc.log
import wc.url


class HttpProxyClient (object):
    """
    A class buffering all incoming data from a server for later use.
    Used to fetch javascript content in background.
    On completion the handler function is called.
    Buffered data is None on error, else the content string.
    """

    def __init__ (self, handler, args, localhost):
        """
        Args is a tuple (url, JS version).
        """
        self.handler = handler
        self.args = args
        self.method = "GET"
        self.decoders = []
        self.url = wc.url.url_norm(self.args[0])[0]
        self.scheme, self.hostname, self.port, self.document = \
                                                  wc.url.url_split(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        self.connected = True
        self.addr = ('#wc_proxy_client#', 80)
        self.localhost = localhost
        self.isredirect = False
        self.headers = wc.http.header.WcMessage()
        attrs = wc.filter.get_filterattrs(self.url, self.localhost,
                                          [wc.filter.STAGE_REQUEST])
        # note: use HTTP/1.0 for JavaScript
        request = "GET %s HTTP/1.0" % self.url
        for stage in wc.proxy.HttpClient.FilterStages:
            request = wc.filter.applyfilter(stage, request, "filter", attrs)
        self.request = request
        assert wc.log.debug(wc.LOG_PROXY, '%s init', self)

    def __repr__ (self):
        """
        Object representation.
        """
        if self.handler is None:
            handler = "None"
        else:
            handler = self.handler.func_name
            if hasattr(self.handler, 'im_class'):
                handler = self.handler.im_class.__name__+"."+handler
        return '<%s: %s %s>' % ('proxyclient', self.args[0], handler)

    def flush_coders (self, coders, data=""):
        while coders:
            assert wc.log.debug(wc.LOG_PROXY, "flush %s", coders[0])
            data = coders[0].process(data)
            data += coders[0].flush()
            del coders[0]
        return data

    def finish (self):
        """
        Tell handler all data is written and remove handler.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s finish', self)
        data = self.flush_coders(self.decoders)
        if self.handler:
            if data:
                self.handler(data, *self.args)
            self.handler(None, *self.args)
            self.handler = None

    def error (self, status, msg, txt=''):
        """
        On error the client finishes.
        """
        wc.log.warn(wc.LOG_PROXY, '%s error %s %s %s',
                     self, status, msg, txt)
        self.finish()

    def write (self, data):
        """
        Give data to handler.
        """
        for decoder in self.decoders:
            data = decoder.process(data)
        if self.handler and data:
            self.handler(data, *self.args)

    def server_response (self, server, response, status, headers):
        """
        Follow redirects, and finish on errors. For HTTP status 2xx continue.
        """
        self.server = server
        assert self.server.connected
        assert wc.log.debug(wc.LOG_PROXY,
                            '%s server_response %r', self, response)
        version, status, msg = \
               wc.http.parse_http_response(response, self.args[0])
        # XXX check version
        assert wc.log.debug(wc.LOG_PROXY, '%s response %s %d %s',
                     self, version, status, msg)
        if status in (302, 301):
            self.isredirect = True
        elif not (200 <= status < 300):
            assert wc.log.debug(wc.LOG_PROXY, "%s got %s status %d %r",
                         self, version, status, msg)
            self.finish()
        if headers.has_key('Transfer-Encoding'):
            # XXX don't look at value, assume chunked encoding for now
            assert wc.log.debug(wc.LOG_PROXY, '%s Transfer-encoding %r',
                         self, headers['Transfer-encoding'])
            unchunker = wc.proxy.decoder.UnchunkStream.UnchunkStream(self)
            self.decoders.append(unchunker)

    def write_trailer (self, data):
        pass

    def server_content (self, data):
        """
        Delegate server content to handler if it is not from a redirect
        response.
        """
        assert self.server
        assert wc.log.debug(wc.LOG_PROXY, '%s server_content with %d bytes',
                     self, len(data))
        if data and not self.isredirect:
            self.write(data)

    def server_close (self, server):
        """
        The server has closed. Either redirect to new url, or finish.
        """
        assert self.server
        assert wc.log.debug(wc.LOG_PROXY, '%s server_close', self)
        if self.isredirect:
            self.redirect()
        else:
            self.finish()

    def server_abort (self):
        """
        The server aborted, so finish.
        """
        assert wc.log.debug(wc.LOG_PROXY, '%s server_abort', self)
        self.finish()

    def handle_local (self):
        """
        Local data is not allowed here, finish.
        """
        wc.log.error(wc.LOG_PROXY, "%s handle_local %s", self, self.args)
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
        self.url = wc.url.url_norm(url)[0]
        self.args = (self.url, self.args[1])
        self.isredirect = False
        assert wc.log.debug(wc.LOG_PROXY, "%s redirected", self)
        self.scheme, self.hostname, self.port, self.document = \
                                                  wc.url.url_split(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        host = wc.url.stripsite(self.url)[0]
        mime_types = self.server.mime_types
        content = ''
        # note: use HTTP/1.0 for JavaScript
        request = "GET %s HTTP/1.0" % self.url
        # close the server and try again
        self.server = None
        headers = wc.proxy.Headers.get_wc_client_headers(host)
        headers['Accept-Encoding'] = 'identity\r'
        wc.proxy.ClientServerMatchmaker.ClientServerMatchmaker(
                    self, request, headers, content, mime_types=mime_types)
