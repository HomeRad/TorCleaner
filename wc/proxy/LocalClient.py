from HttpClient import HttpClient
from wc.webgui import WebConfig
import cgi
from cStringIO import StringIO

class LocalClient (HttpClient):
    """delegate all requests to the web config class"""
    def server_request (self):
        assert self.state == 'receive'
        # reject invalid methods
        if self.method not in ['GET', 'POST', 'HEAD']:
            return self.error(403, i18n._("Invalid Method"))
        # get cgi form data
        # XXX uses FieldStorage internals
        form = cgi.FieldStorage(fp=StringIO(self.content),
                                headers=self.headers,
                                environ={'REQUEST_METHOD': self.method})
        # this object will call server_connected at some point
        WebConfig(self, self.url, form, self.protocol)
