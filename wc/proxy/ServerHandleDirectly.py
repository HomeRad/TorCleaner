import rfc822
from cStringIO import StringIO
from Server import Server

class ServerHandleDirectly(Server):
    def __init__(self, client, response, headers, content):
        Server.__init__(self, client)
        headers = "Content-Length: %d\r\n%s" % (len(content), headers)
        headers = rfc822.Message(StringIO(headers))
        self.connected = 1
        client.server_response(self, response, headers)
        client.server_content(content)
        client.server_close()
        self.connected = 0
