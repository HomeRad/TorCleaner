import rfc822
from cStringIO import StringIO
from Server import Server

class ServerHandleDirectly(Server):
    def __init__(self, client, response, headers, content):
        Server.__init__(self, client)
        self.response = response
        self.headers = rfc822.Message(StringIO(headers))
        self.content = content
        # NOTE: we could insert the content-length here
        self.connected = 1
        client.server_response(self, self.response, self.headers)
        client.server_content(self.content)
        client.server_close()
        self.connected = 0
