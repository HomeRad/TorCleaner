from cStringIO import StringIO
from Server import Server
from Headers import WcMessage

class ServerHandleDirectly (Server):
    def __init__ (self, client, response, headers, content):
        Server.__init__(self, client)
        headers = "Content-Length: %d\r\n%s" % (len(content), headers)
        headers = WcMessage(StringIO(headers))
        self.connected = "True"
        client.server_response(self, response, headers)
        client.server_content(content)
        client.server_close()
        self.connected = None
