# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2007 Bastian Kleineidam
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
Test HTTP request version compatibility.
"""

from tests import make_suite
from wc.proxy.tests import ProxyTest

class HighverTest (ProxyTest):

    def check_response_status (self, response):
        self.assertEqual(response.status, 505)


class test_highver_1_2 (HighverTest):
    """
    Reject 1.2 HTTP version.
    """

    def test_highver_1_2 (self):
        self.start_test()

    def get_request_version (self):
        return (1, 2)


class test_highver_2_1 (HighverTest):
    """
    Reject 2.1 HTTP version.
    """

    def test_highver_2_1 (self):
        self.start_test()

    def get_request_version (self):
        return (2, 1)


class test_highver_1_12 (HighverTest):
    """
    Reject 1.12 HTTP version.
    """

    def test_highver_1_12 (self):
        self.start_test()

    def get_request_version (self):
        return (1, 12)


class test_highver_12_1 (HighverTest):
    """
    Reject 12.1 HTTP version.
    """

    def test_highver_12_1 (self):
        self.start_test()

    def get_request_version (self):
        return (12, 1)


class test_highver_1_011 (HighverTest):
    """
    Reject 1.011 HTTP version.
    """

    def test_highver_1_011 (self):
        self.start_test()

    def construct_request_data (self, request):
        """
        Construct a valid HTTP request data.
        """
        lines = []
        version = "HTTP/1.011"
        lines.append("%s %s %s" % (request.method, request.uri, version))
        lines.extend(request.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if request.content:
            data += request.content
        return data


class test_highver_011_1 (HighverTest):
    """
    Reject 011.1 HTTP version.
    """

    def test_highver_011_1 (self):
        self.start_test()

    def construct_request_data (self, request):
        """
        Construct a valid HTTP request data.
        """
        lines = []
        version = "HTTP/011.1"
        lines.append("%s %s %s" % (request.method, request.uri, version))
        lines.extend(request.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if request.content:
            data += request.content
        return data


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
