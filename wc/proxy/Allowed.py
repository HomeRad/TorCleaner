# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc import config

class AllowedHttpClient (object):
    def __init__ (self):
        self.methods = ['GET', 'HEAD', 'CONNECT', 'POST']
        self.schemes = ['http', 'https'] # 'nntps' is untested
        self.connect_ports = [443] # 563 (NNTP over SSL) is untested
        self.public_docs = [
          '/blocked.html',
          '/blocked.png',
          '/error.html',
          '/wc.css',
          '/adminpass.html',
          '/rated.html',
          '/robots.txt',
        ]


    def method (self, meth):
        return meth in self.methods


    def scheme (self, schem):
        return schem in self.schemes


    def public_document (self, doc):
        for f in self.public_docs:
            if doc.startswith(f):
                return True
        return False


    def host (self, host):
        return config.allowed(host)


    def connect_port (self, port):
        return port in self.connect_ports



class AllowedSslClient (AllowedHttpClient):
    def __init__ (self):
        super(AllowedSslClient, self).__init__()
        self.methods = ['GET', 'HEAD', 'POST']
        self.schemes = ['https']
        self.connect_ports = []
