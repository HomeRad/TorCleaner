# -*- coding: iso-8859-1 -*-
"""
Allowance classes to filter out invalid proxy requests.
"""

import wc
import wc.configuration


class AllowedHttpClient (object):
    """
    Allowance data for http clients.
    """

    def __init__ (self):
        """
        Initialize allowances.
        """
        self.methods = ['GET', 'HEAD', 'CONNECT', 'POST']
        self.schemes = ['http', 'https'] # 'nntps' is untested

        self.connect_ports = [443] # 563 (NNTP over SSL) is untested
        self.http_ports = [80, 81, 8080, 8081, 3128]
        self.public_docs = [
          '/blocked.html',
          '/blocked.png',
          '/blocked.swf',
          '/blocked.js',
          '/error.html',
          '/favicon.ico',
          '/favicon.png',
          '/wc.css',
          '/adminpass.html',
          '/rated.html',
          '/robots.txt',
        ]

    def public_document (self, doc):
        """
        Return True iff doc is a public document.
        """
        for f in self.public_docs:
            if doc.startswith(f):
                return True
        return False

    def host (self, host):
        """
        Return True iff host is allowed.
        """
        return wc.configuration.config.allowed(host)

    def method (self, method):
        return method in self.methods

    def is_allowed (self, method, scheme, port):
        if not self.method(method):
            wc.log.warn(wc.LOG_PROXY, "illegal method %s", method)
            return False
        if scheme not in self.schemes:
            wc.log.warn(wc.LOG_PROXY, "illegal scheme %s", scheme)
            return False
        if method == 'CONNECT':
            # CONNECT method sanity
            if port not in self.connect_ports:
                wc.log.warn(wc.LOG_PROXY, "illegal CONNECT port %d", port)
                return False
            if scheme != 'https':
                wc.log.warn(wc.LOG_PROXY, "illegal CONNECT scheme %d", scheme)
                return False
        else:
            # all other methods
            if port not in self.http_ports:
                wc.log.warn(wc.LOG_PROXY, "illegal port %d", port)
                return False
        return True


class AllowedSslClient (AllowedHttpClient):
    """
    Allowance data for ssl clients.
    """

    def __init__ (self):
        """
        Initialize allowances.
        """
        super(AllowedSslClient, self).__init__()
        self.methods = ['GET', 'HEAD', 'POST']
        self.schemes = ['https']
        self.connect_ports = []
