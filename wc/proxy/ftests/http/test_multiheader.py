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
Test handling of multiple headers.
"""

from wc.proxy.ftests import ProxyTest, make_suite


class test_multiheader_clen_toclient (ProxyTest):
    """
    Only one Content-Length is allowed. This disables HTTP request
    smuggling attacks.
    """

    def test_multiheader_clen_toclient (self):
        self.start_test()

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
            headers.append("Content-Length: %d" % (len(content)-5))
        return headers

    def check_request_headers (self, request):
        num_found = 0
        for header in request.headers:
            if header.lower().startswith("content-length:"):
                num_found += 1
        self.assert_(num_found < 2)


class test_multiheader_clen_toserver (ProxyTest):
    """
    Only one Content-Length is allowed. This disables HTTP request
    smuggling attacks.
    """

    def test_multiheader_clen_toserver (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Content-Length: %d" % (len(content)-5),
        ]

    def check_response_headers (self, response):
        num_found = 0
        for header in response.headers:
            if header.lower().startswith("content-length:"):
                num_found += 1
        self.assert_(num_found < 2)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())

