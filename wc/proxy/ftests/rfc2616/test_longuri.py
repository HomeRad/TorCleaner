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
Test long URIs.
"""

from wc.proxy.ftests import ProxyTest, make_suite


class LonguriTest (ProxyTest):

    def longuri (self, bytes):
        octets = int(bytes / 8)
        remainder = max(0, (bytes % 8) - 1)
        return "/%s%s" % ("01234567" * octets, "x"*remainder)

    def check_response_status (self, response):
        self.assert_(response.status in (200, 414))


class test_longuri_1024 (LonguriTest):
    """
    Test 1024 byte URI.
    """

    def test_longuri_1024 (self):
        self.start_test()

    def get_request_uri (self):
        return self.longuri(1024)


class test_longuri_8192 (LonguriTest):
    """
    Test 8192 byte URI.
    """

    def test_longuri_8192 (self):
        self.start_test()

    def get_request_uri (self):
        return self.longuri(8192)


class test_longuri_65536 (LonguriTest):
    """
    Test 65536 byte URI.
    """

    def test_longuri_65536 (self):
        self.start_test()

    def get_request_uri (self):
        return self.longuri(65536)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
