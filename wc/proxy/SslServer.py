# -*- coding: iso-8859-1 -*-
"""connection handling WebCleaner SSL server <--> Remote SSL server"""

import socket
import wc
import wc.configuration
import wc.proxy.HttpServer
import wc.proxy.SslConnection
import wc.proxy.ssl
import wc.log


class SslServer (wc.proxy.HttpServer.HttpServer,
                 wc.proxy.SslConnection.SslConnection):
    """Server object for SSL connections. Since this class must not have Proxy
       functionality, the header mangling is different."""

    def __init__ (self, ipaddr, port, client):
        """initialize connection object and connect to remove server"""
        super(wc.proxy.HttpServer.HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.reset()
        # attempt connect
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM,
         sslctx=wc.proxy.ssl.get_clientctx(wc.configuration.config.configdir))
        self.socket.settimeout(wc.config['timeout'])
        self.try_connect()
        self.socket.set_connect_state()

    def __repr__ (self):
        """object description"""
        if self.addr[1] != 80:
            portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        extra = '%s%s' % (self.addr[0], portstr)
        if self.socket:
            extra += " (%s)" % self.socket.state_string()
        if not self.connected:
            extra += " (unconnected)"
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('sslserver', self.state, extra)

    def mangle_request_headers (self):
        """modify HTTP request headers"""
        # nothing to do
        pass

    def mangle_response_headers (self):
        """modify HTTP response headers"""
        self.bytes_remaining = wc.proxy.Headers.server_set_encoding_headers(
         self.headers, self.is_rewrite(), self.decoders, self.bytes_remaining)
        if self.bytes_remaining is None:
            self.persistent = False
        # 304 Not Modified does not send any type info, because it was cached
        if self.statuscode != 304:
            # copy decoders
            decoders = [d.__class__() for d in self.decoders]
            data = self.recv_buffer
            for decoder in decoders:
                data = decoder.decode(data)
            data += wc.proxy.HttpServer.flush_decoders(decoders)
            wc.proxy.Headers.server_set_content_headers(
                                        self.headers, self.mime, self.url)

    def process_recycle (self):
        """recycle this server connection into the connection pool"""
        wc.log.debug(wc.LOG_PROXY, "%s recycling", self)
        # flush pending client data and try to reuse this connection
        self.delayed_close()
