from wc.log import *
from HttpClient import HttpClient
from wc.webgui import WebConfig
from ClientServerMatchmaker import ClientServerMatchmaker
from SslConnection import SslConnection
from Allowed import AllowedSslClient
from wc.url import spliturl, url_norm


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
        self.allow = AllowedSslClient()


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


    def fix_request (self):
        # refresh with filtered request data
        self.method, self.url, self.protocol = self.request.split()
        # enforce a maximum url length
        if len(self.url) > 1024:
            error(PROXY, "%s request url length %d chars is too long", self, len(self.url))
            self.error(400, i18n._("URL too long"))
            return False
        if len(self.url) > 255:
            warn(PROXY, "%s request url length %d chars is very long", self, len(self.url))
        # and unquote again
        self.url = url_norm(self.url)
        self.scheme, self.hostname, self.port, self.document = spliturl(self.url)
        # fix missing trailing /
        if not self.document:
            self.document = '/'
        # some clients send partial URI's without scheme, hostname
        # and port to clients, so we have to handle this
        if not self.scheme:
            # default scheme is https
            self.scheme = 'https'
        if not self.allow.scheme(self.scheme):
            warn(PROXY, "%s forbidden scheme %r encountered", self, self.scheme)
            self.error(403, i18n._("Forbidden"))
            return False
        # request is ok
        return True


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

