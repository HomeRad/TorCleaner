# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from cStringIO import StringIO
from Server import Server
from Headers import WcMessage

class ServerHandleDirectly (Server):
    def __init__ (self, client, response, headers, content):
        super(ServerHandleDirectly, self).__init__(client, 'default')
        headers = "Content-Length: %d\r\n%s" % (len(content), headers)
        headers = WcMessage(StringIO(headers))
        self.connected = True
        client.server_response(self, response, headers)
        client.server_content(content)
        client.server_close()
        self.connected = False


    def process_connect (self):
        pass
