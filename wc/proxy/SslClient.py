# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
SSL client connection.
"""

import wc
import wc.webgui
import wc.proxy.HttpClient
import wc.proxy.ClientServerMatchmaker
import wc.proxy.SslConnection
import wc.proxy.Allowed
import wc.log
import wc.url


class SslClient (wc.proxy.HttpClient.HttpClient,
                 wc.proxy.SslConnection.SslConnection):
    """
    Handle SSL server requests, no proxy functionality is here.
    Response data will be encrypted with the WebCleaner SSL server
    certificate. The browser will complain about differing certificate
    domains, which is the price to pay for an SSL gateway.
    Despite having no proxying capabilities, this class is inherited
    from HttpClient.
    """

    def __init__ (self, sock, addr):
        super(SslClient, self).__init__(sock, addr)
        self.allow = wc.proxy.Allowed.AllowedSslClient()

    def fix_request (self):
        # refresh with filtered request data
        self.method, self.url, self.protocol = self.request.split()
        # enforce a maximum url length
        if len(self.url) > 2048:
            wc.log.error(wc.LOG_PROXY,
                         "%s request url length %d chars is too long",
                         self, len(self.url))
            self.error(400, _("URL too long"),
                       txt=_('URL length limit is %d bytes.') % 2048)
            return False
        if len(self.url) > 255:
            wc.log.warn(wc.LOG_PROXY,
                        "%s request url length %d chars is very long",
                        self, len(self.url))
        # and unquote again
        self.url = wc.url.url_norm(self.url)[0]
        self.scheme, self.hostname, self.port, self.document = \
                                                wc.url.url_split(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        # some clients send partial URI's without scheme, hostname
        # and port to clients, so we have to handle this
        if not self.scheme:
            self.scheme = "https"
        if not self.allow.is_allowed(self.method, self.scheme, self.port):
            wc.log.warn(wc.LOG_PROXY, "Unallowed request %s", self.url)
            self.error(403, _("Forbidden"))
            return False
        # request is ok
        return True

    def server_request (self):
        assert self.state == 'receive', \
                      "%s server_request in non-receive state" % self
        wc.log.debug(wc.LOG_PROXY, "%s server_request", self)
        # this object will call server_connected at some point
        wc.proxy.ClientServerMatchmaker.ClientServerMatchmaker(
              self, self.request, self.headers, self.content, sslserver=True)

    def handle_local (self, is_public_doc=False):
        assert self.state == 'receive'
        wc.log.debug(wc.LOG_PROXY, '%s handle_local', self)
        form = None
        self.url = "/blocked.html"
        self.headers['Host'] = '%s\r' % self.socket.getsockname()[0]
        wc.webgui.WebConfig(self, self.url, form, self.protocol, self.headers)

    def mangle_request_headers (self, headers):
        # nothing to do
        pass
