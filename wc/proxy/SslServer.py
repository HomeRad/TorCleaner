# -*- coding: iso-8859-1 -*-
"""connection handling WebCleaner SSL server <--> Remote SSL server"""

import socket
from wc import config
from wc.log import *
from HttpServer import HttpServer, flush_decoders
from SslConnection import SslConnection
from Headers import server_set_encoding_headers, server_set_content_headers
from ssl import get_clientctx


class SslServer (HttpServer, SslConnection):
    """Server object for SSL connections. Since this class must not have Proxy
       functionality, the header mangling is different."""

    def __init__ (self, ipaddr, port, client):
        """initialize connection object and connect to remove server"""
        super(HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.reset()
        # attempt connect
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=get_clientctx())
        self.socket.settimeout(config['timeout'])
        self.connect(self.addr)
        self.socket.set_connect_state()


    def __repr__ (self):
        """object description"""
        if self.addr[1] != 80:
	    portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        extra = '%s%s' % (self.addr[0], portstr)
        if self.socket:
            extra += " (%s)"%self.socket.state_string()
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
        self.bytes_remaining = server_set_encoding_headers(self.headers, self.is_rewrite(), self.decoders, self.bytes_remaining)
        if self.bytes_remaining is None:
            self.persistent = False
        # 304 Not Modified does not send any type info, because it was cached
        if self.statuscode!=304:
            # copy decoders
            decoders = [d.__class__() for d in self.decoders]
            data = self.recv_buffer
            for decoder in decoders:
                data = decoder.decode(data)
            data += flush_decoders(decoders)
            server_set_content_headers(self.headers, data, self.document,
                                       self.mime, self.url)


    def process_recycle (self):
        """recycle this server connection into the connection pool"""
        debug(PROXY, "%s recycling", self)
        # flush pending client data and try to reuse this connection
        self.delayed_close()

