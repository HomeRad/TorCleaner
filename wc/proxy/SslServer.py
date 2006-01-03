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
Connection handling WebCleaner SSL server <--> Remote SSL server.
"""

import socket

import wc
import wc.configuration
import wc.proxy.HttpServer
import wc.proxy.SslConnection
import wc.proxy.ssl
import wc.log
import OpenSSL.SSL

class SslServer (wc.proxy.HttpServer.HttpServer,
                 wc.proxy.SslConnection.SslConnection):
    """
    Server object for SSL connections. Since this class must not have Proxy
    functionality, the header mangling is different.
    """

    def __init__ (self, ipaddr, port, client):
        """
        Initialize connection object and connect to remove server.
        """
        super(wc.proxy.HttpServer.HttpServer, self).__init__(client,
                                                             'connect')
        # default values
        self.addr = (ipaddr, port)
        self.create_socket(self.get_family(ipaddr), socket.SOCK_STREAM)
        sslctx = wc.proxy.ssl.get_clientctx(wc.configuration.config.configdir)
        self.socket = OpenSSL.SSL.Connection(sslctx, self.socket)
        self.socket.set_connect_state()
        # attempt connect
        self.try_connect()

    def mangle_request_headers (self):
        """
        Modify HTTP request headers.
        """
        # nothing to do
        pass

    def mangle_response_headers (self):
        """
        Modify HTTP response headers.
        """
        self.bytes_remaining = \
            wc.proxy.Headers.server_set_encoding_headers(self)
        if self.bytes_remaining is None:
            self.persistent = False
        if self.statuscode == 304:
            # 304 Not Modified does not send any type info, because it
            # was cached
            return
        wc.proxy.Headers.server_set_content_headers(
                                     self.headers, self.mime_types, self.url)

    def process_recycle (self):
        """
        Recycle this server connection into the connection pool.
        """
        assert wc.log.debug(wc.LOG_PROXY, "%s recycling", self)
        # flush pending client data and try to reuse this connection
        self.delayed_close()
