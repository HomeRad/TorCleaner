# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

import wc
import wc.configuration


MAX_URL_LEN = 8192


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

        self.connect_ports = [443] # 563 (NNTP over SSL) is untested
        self.http_ports = [80, 81, 8000, 8080, 8081, 8090, 3128]
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
        self.http_ports.append(443)
