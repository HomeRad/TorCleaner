# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Connection handling WebCleaner SSL server <--> Remote SSL server.
"""

import socket

from . import HttpServer, Headers, SslConnection, ssl
from .. import log, LOG_PROXY, configuration
from OpenSSL import SSL

class SslServer(HttpServer.HttpServer, SslConnection.SslConnection):
    """
    Server object for SSL connections. Since this class must not have Proxy
    functionality, the header mangling is different.
    """

    def __init__(self, ipaddr, port, client):
        """
        Initialize connection object and connect to remove server.
        """
        super(HttpServer.HttpServer, self).__init__(client,
                                                             'connect')
        # default values
        self.addr = (ipaddr, port)
        self.create_socket(self.get_family(ipaddr), socket.SOCK_STREAM)
        sslctx = ssl.get_clientctx(configuration.config.configdir)
        self.socket = SSL.Connection(sslctx, self.socket)
        self.socket.set_connect_state()
        # attempt connect
        self.try_connect()

    def mangle_request_headers(self):
        """
        Modify HTTP request headers.
        """
        # nothing to do
        pass

    def mangle_response_headers(self):
        """
        Modify HTTP response headers.
        """
        self.bytes_remaining = Headers.server_set_encoding_headers(self)
        if self.bytes_remaining is None:
            self.persistent = False
        if self.statuscode == 304:
            # 304 Not Modified does not send any type info, because it
            # was cached
            return
        Headers.server_set_content_headers(
                    self.statuscode, self.headers, self.mime_types, self.url)

    def process_recycle(self):
        """
        Recycle this server connection into the connection pool.
        """
        log.debug(LOG_PROXY, "%s recycling", self)
        # flush pending client data and try to reuse this connection
        self.delayed_close()
