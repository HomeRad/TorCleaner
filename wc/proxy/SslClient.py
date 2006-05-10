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

    def get_default_scheme (self):
        return "https"

    def server_request (self):
        assert self.state == 'receive', \
                      "%s server_request in non-receive state" % self
        assert None == wc.log.debug(wc.LOG_PROXY, "%s server_request", self)
        # this object will call server_connected at some point
        wc.proxy.ClientServerMatchmaker.ClientServerMatchmaker(
              self, self.request, self.headers, self.content, sslserver=True)

    def handle_local (self, is_public_doc=False):
        assert self.state == 'receive'
        assert None == wc.log.debug(wc.LOG_PROXY, '%s handle_local', self)
        form = None
        self.url = "/blocked.html"
        self.headers['Host'] = '%s\r' % self.socket.getsockname()[0]
        wc.webgui.WebConfig(self, self.url, form,
                            self.protocol, self.headers).send()

    def mangle_request_headers (self, headers):
        # nothing to do
        pass
