from HttpClient import HttpClient

class LocalClient (HttpClient):
    """delegate all requests to the web config class"""
    def server_request (self):
        assert self.state == 'receive'
        # This object will call server_connected at some point
        WebConfig(self, self.request, self.headers, self.content)
