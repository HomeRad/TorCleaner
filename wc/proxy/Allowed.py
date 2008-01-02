# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2008 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Allowance classes to filter out invalid proxy requests.
"""

import wc.configuration


MAX_URL_LEN = 8192


def allowed_connect_port (port):
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


def is_in_document_list (doc, docs):
    """
    Return True iff doc is document list.
    """
    for f in docs:
        if doc.startswith(f):
            return True
    return False


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

    def public_document (self, doc):
        """
        Return True iff doc is a public document.
        """
        return is_in_document_list(doc, self.public_docs)

    def admin_document (self, doc):
        """
        Return True iff doc is an admin document.
        """
        return is_in_document_list(doc, self.admin_docs)

    def host (self, host):
        """
        Return True iff host is allowed.
        """
        return wc.configuration.config.allowed(host)

    def method (self, method):
        """
        Check if givem method is allowed.
        """
        return method in self.methods

    def is_allowed (self, method, scheme, port):
        """
        Check if givem method, scheme and port are allowed.
        """
        if not self.method(method):
            wc.log.warn(wc.LOG_PROXY, "illegal method %s", method)
            return False
        if scheme not in self.schemes:
            wc.log.warn(wc.LOG_PROXY, "illegal scheme %s", scheme)
            return False
        if method == 'CONNECT':
            if scheme != 'https':
                wc.log.warn(wc.LOG_PROXY, "illegal CONNECT scheme %d", scheme)
                return False
            if not allowed_connect_port(port):
                wc.log.warn(wc.LOG_PROXY, "illegal CONNECT port %d", port)
                return False
            if port not in (443, 563):
                wc.log.warn(wc.LOG_PROXY, "Unusual CONNECT port %d", port)
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
