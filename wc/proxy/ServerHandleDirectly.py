# -*- coding: iso-8859-1 -*-
"""direct request handling returning static data"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.proxy.Server import Server

class ServerHandleDirectly (Server):
    """Answer a server request with static data"""

    def __init__ (self, client, response, status, headers, content):
        """write given response to client"""
        super(ServerHandleDirectly, self).__init__(client, 'default')
        if content:
            headers["Content-Length"] = "%d\r" % len(content)
        self.connected = True
        client.server_response(self, response, status, headers)
        client.server_content(content)
        client.server_close(self)
        self.connected = False


    def process_connect (self):
        """empty function; no server connection has to be made"""
        pass


    def process_read (self):
        """empty function; no server has to be read"""
        pass
