# -*- coding: iso-8859-1 -*-
"""connection handling SSL client <--> proxy"""

import os, socket
from wc import ConfigDir, config
from wc.log import *
from ssl import clientctx
from StatefulConnection import StatefulConnection
from HttpServer import HttpServer
from Connection import MAX_BUFSIZE, RECV_BUFSIZE, SEND_BUFSIZE
from OpenSSL import SSL


class HttpsServer (HttpServer):
    """XXX """
    def __init__ (self, ipaddr, port, client):
        super(HttpServer, self).__init__(client, 'connect')
        # default values
        self.addr = (ipaddr, port)
        self.reset()
        assert config['sslgateway'], "%s unwanted ssl gateway usage"%str(self)
        # attempt connect
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=clientctx)
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
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('https server', self.state, extra)


    def handle_read (self):
        """read data from connection, put it into recv_buffer and call
           process_read"""
        assert self.connected
        debug(PROXY, '%s HttpsClient.handle_read', self)
	if len(self.recv_buffer) > MAX_BUFSIZE:
            warn(PROXY, '%s read buffer full', self)
	    return
        try:
            data = self.recv(RECV_BUFSIZE)
        except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError):
            debug(PROXY, "%s ssl read message", self)
            return
        except SSL.ZeroReturnError:
            self.close()
            return
        except SSL.Error, err:
            self.handle_error('read error')
            return
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            debug(PROXY, "%s closed, got empty data", self)
            return
        debug(PROXY, '%s <= read %d', self, len(data))
        debug(CONNECTION, 'data %r', data)
	self.recv_buffer += data
        self.process_read()


    def handle_write (self):
        """Write data from send_buffer to connection socket.
           Execute a possible pending close."""
        assert self.connected
        assert self.send_buffer
        debug(PROXY, '%s handle_write', self)
        num_sent = 0
        data = self.send_buffer[:SEND_BUFSIZE]
        try:
            num_sent = self.send(data)
        except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError):
            debug(PROXY, "%s ssl write message", self)
            return
        except SSL.Error, err:
            self.handle_error('write error')
            return
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('write error')
            return
        debug(PROXY, '%s => wrote %d', self, num_sent)
        debug(CONNECTION, 'data %r', data)
        self.send_buffer = self.send_buffer[num_sent:]
        if self.close_pending and self.close_ready():
            self.close()

