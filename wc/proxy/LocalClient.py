from HttpClient import HttpClient
from wc.webgui import WebConfig
import cgi
from cStringIO import StringIO

class LocalClient (HttpClient):
    """delegate all requests to the web config class"""
    def server_request (self):
        assert self.state == 'receive'
        method, url, protocol = request.split()
        # reject invalid methods
        if method not in ['GET', 'POST', 'HEAD']:
            return self.error(403, i18n._("Invalid Method"))
        # get cgi form data
        # XXX this exploits FieldStorage internals
        form = cgi.FieldStorage(fp=StringIO(self.content),
                                headers=self.headers,
                                environ={'REQUEST_METHOD': method})
        # This object will call server_connected at some point
        WebConfig(self, url, form)
