# -*- coding: iso-8859-1 -*-
"""Allowance classes to filter out infalid proxy requests"""

import wc


class AllowedHttpClient (object):
    """Allowance data for http clients"""

    def __init__ (self):
        """initialize allowances"""
        self.methods = ['GET', 'HEAD', 'CONNECT', 'POST']
        self.schemes = ['http', 'https'] # 'nntps' is untested
        self.connect_ports = [443] # 563 (NNTP over SSL) is untested
        self.public_docs = [
          '/blocked.html',
          '/blocked.png',
          '/blocked.swf',
          '/blocked.js',
          '/error.html',
          '/wc.css',
          '/adminpass.html',
          '/rated.html',
          '/robots.txt',
        ]


    def method (self, meth):
        """return True iff method is allowed"""
        return meth in self.methods


    def scheme (self, schem):
        """return True iff scheme is allowed"""
        return schem in self.schemes


    def public_document (self, doc):
        """return True iff doc is a public document"""
        for f in self.public_docs:
            if doc.startswith(f):
                return True
        return False


    def host (self, host):
        """return True iff host is allowed"""
        return wc.config.allowed(host)


    def connect_port (self, port):
        """return True iff port is a valid port for CONNECT method"""
        return port in self.connect_ports



class AllowedSslClient (AllowedHttpClient):
    """Allowance data for ssl clients"""

    def __init__ (self):
        """initialize allowances"""
        super(AllowedSslClient, self).__init__()
        self.methods = ['GET', 'HEAD', 'POST']
        self.schemes = ['https']
        self.connect_ports = []
