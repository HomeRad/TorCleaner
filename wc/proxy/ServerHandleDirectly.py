# -*- coding: iso-8859-1 -*-
"""
Direct request handling returning static data.
"""

import wc.proxy.Server


class ServerHandleDirectly (wc.proxy.Server.Server):
    """
    Answer a server request with static data.
    """

    def __init__ (self, client, response, status, headers, content):
        """
        Write given response to client.
        """
        super(ServerHandleDirectly, self).__init__(client, 'default')
        if content:
            headers["Content-Length"] = "%d\r" % len(content)
        self.connected = True
        client.server_response(self, response, status, headers)
        client.server_content(content)
        client.server_close(self)
        self.connected = False

    def process_connect (self):
        """
        Empty function; no server connection has to be made.
        """
        pass

    def process_read (self):
        """
        Empty function; no server has to be read.
        """
        pass
