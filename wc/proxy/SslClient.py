import os, socket, errno
from wc import ConfigDir
from wc.log import *
from HttpClient import HttpClient
from Connection import MAX_BUFSIZE, RECV_BUFSIZE
from OpenSSL import SSL
from wc.webgui import WebConfig
from ClientServerMatchmaker import ClientServerMatchmaker


class SslClient (HttpClient):
    """Handle SSL server requests, no proxy functionality is here.
       Response data will be encrypted with the WebCleaner SSL server
       certificate. The browser will complain about differing certificate
       domains, which is the price to pay for an SSL gateway.
       Despite having no proxying capabilities, this class is inherited
       from HttpClient.
    """

    def __init__ (self, sock, addr):
        super(SslClient, self).__init__(sock, addr)
        debug(PROXY, "%s init with %s", self, addr)


    def __repr__ (self):
        extra = self.persistent and "persistent " or ""
        if self.request:
            try:
                extra += self.request.split()[1]
            except IndexError:
                extra += '???'+self.request
        else:
            extra += 'being read'
        return '<%s:%-8s %s>'%('sslclient', self.state, extra)


    def server_request (self):
        assert self.state=='receive', "%s server_request in non-receive state"%self
        debug(PROXY, "%s server_request", self)
        # this object will call server_connected at some point
        ClientServerMatchmaker(self, self.request, self.headers, self.content)


    def handle_local (self):
        assert self.state=='receive'
        debug(PROXY, '%s handle_local', self)
        form = None
        self.url = "/blocked.html"
        self.headers['Host'] = 'localhost\r'
        WebConfig(self, self.url, form, self.protocol, self.headers)


    def handle_read (self):
        """read data from SSL connection, put it into recv_buffer and call
           process_read"""
        assert self.connected
        debug(PROXY, '%s Connection.handle_read', self)
	if len(self.recv_buffer) > MAX_BUFSIZE:
            warn(PROXY, '%s read buffer full', self)
	    return
        try:
            data = self.recv(RECV_BUFSIZE)
        except socket.error, err:
            if err==errno.EAGAIN:
                # try again later
                return
            self.handle_error('read error')
            return
        except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError), err:
            exception(PROXY, "%s ssl read message", self)
            return
        except (SSL.Error, SSL.ZeroReturnError), err:
            self.handle_error('read error')
            return
        if not data: # It's been closed, and handle_close has been called
            debug(PROXY, "%s closed, got empty data", self)
            return
        debug(PROXY, '%s <= read %d', self, len(data))
        debug(CONNECTION, 'data %r', data)
	self.recv_buffer += data
        self.process_read()
