# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Allowance classes to filter out invalid proxy requests.
"""

from .. import log, LOG_PROXY, configuration


MAX_URL_LEN = 8192


def allowed_connect_port(port):
    """
    Tell if the given port number is allowed in a CONNECT method.

    @param port: port number
    @type port: integer
    @return: port is allowed or not
    @rtype: boolean
    """
    if port in (443, 563):
        # https and snews
        return True
    # high port
    return 1024 <= port <= 65535


def is_in_document_list(doc, docs):
    """
    Return True iff doc is document list.
    """
    for f in docs:
        if doc.startswith(f):
            return True
    return False


class AllowedHttpClient(object):
    """
    Allowance data for http clients.
    """

    def __init__(self):
        """
        Initialize allowances.
        """
        self.methods = ['GET', 'HEAD', 'CONNECT', 'POST']
        self.schemes = ['http', 'https'] # 'nntps' is untested

        self.public_docs = [
          '/blocked.html',
          '/blocked.png',
          '/blocked.swf',
          '/blocked.js',
          '/error.html',
          '/favicon.ico',
          '/favicon.png',
          '/wc.css',
          '/rated.html',
          '/robots.txt',
        ]
        # documents to visit when no admin password has been given
        self.admin_docs = [
          '/adminpass.html',
          '/restart_ask.html',
          '/restart.html',
        ]

    def public_document(self, doc):
        """
        Return True iff doc is a public document.
        """
        return is_in_document_list(doc, self.public_docs)

    def admin_document(self, doc):
        """
        Return True iff doc is an admin document.
        """
        return is_in_document_list(doc, self.admin_docs)

    def host(self, host):
        """
        Return True iff host is allowed.
        """
        return configuration.config.allowed(host)

    def method(self, method):
        """
        Check if givem method is allowed.
        """
        return method in self.methods

    def is_allowed(self, method, scheme, port):
        """
        Check if givem method, scheme and port are allowed.
        """
        if not self.method(method):
            log.warn(LOG_PROXY, "illegal method %s", method)
            return False
        if scheme not in self.schemes:
            log.warn(LOG_PROXY, "illegal scheme %s", scheme)
            return False
        if method == 'CONNECT':
            if scheme != 'https':
                log.warn(LOG_PROXY, "illegal CONNECT scheme %d", scheme)
                return False
            if not allowed_connect_port(port):
                log.warn(LOG_PROXY, "illegal CONNECT port %d", port)
                return False
            if port not in (443, 563):
                log.warn(LOG_PROXY, "Unusual CONNECT port %d", port)
        return True


class AllowedSslClient(AllowedHttpClient):
    """
    Allowance data for ssl clients.
    """

    def __init__(self):
        """
        Initialize allowances.
        """
        super(AllowedSslClient, self).__init__()
        self.methods = ['GET', 'HEAD', 'POST']
        self.schemes = ['https']
