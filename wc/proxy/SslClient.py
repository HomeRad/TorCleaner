from wc.log import *
from HttpClient import HttpClient
from wc.webgui import WebConfig
from ClientServerMatchmaker import ClientServerMatchmaker
from SslConnection import SslConnection


class SslClient (HttpClient, SslConnection):
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

