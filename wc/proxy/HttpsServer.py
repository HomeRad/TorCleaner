# -*- coding: iso-8859-1 -*-
"""connection handling SSL client <--> proxy"""

import socket
from wc import ConfigDir, config
from wc.log import *
from ssl import get_clientctx
from HttpServer import HttpServer
from SslConnection import SslConnection


class HttpsServer (HttpServer, SslConnection):
    """XXX """
    def __init__ (self, ipaddr, port, client):
        super(HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.reset()
        assert config['sslgateway'], "%s unwanted ssl gateway usage"%str(self)
        # attempt connect
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=get_clientctx())
        try:
	    self.connect(self.addr)
        except socket.error:
            self.handle_error('connect error')


    def __repr__ (self):
        """object description"""
        if self.addr[1] != 80:
	    portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        extra = '%s%s' % (self.addr[0], portstr)
        if self.socket:
            extra += " (%s)"%self.socket.state_string()
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('https server', self.state, extra)

