# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from HttpClient import HttpClient

class LocalClient (HttpClient):
    """delegate all requests to the web config class. This is only needed
       for servers running on separate port numbers (see proxy.mainloop
       for an example)."""
    def server_request (self):
        return self.handle_local()
