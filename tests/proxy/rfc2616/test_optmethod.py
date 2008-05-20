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
Test optional methods.
"""

from tests import make_suite
from .. import ProxyTest


class MethodTest (ProxyTest):

    def check_response_status (self, response):
        self.assert_(response.status in (405, 200))

    def check_response_message (self, response):
        pass

    def check_response_method (self, response):
        if response.status == 200:
            self.check_response_method2(response)

    def check_response_method2 (self, response):
        pass

    def check_response_content (self, response):
        if response.status == 200:
            self.assertEquals(response.content, self.get_response_content())


class test_optmethod_options (MethodTest):
    """
    Proxy must implement or reject OPTIONS method.
    """

    def test_optmethod_options (self):
        self.start_test()

    def get_request_method (self):
        return "OPTIONS"

    def check_response_method2 (self, response):
        if response.content:
            # Content-Type must be included
            self.assert_(response.has_header("Content-Type"))
        else:
            self.assert_(response.has_header("Content-Length"))
            self.assertEqual(response.get_header("Content-Length"), "0")


class test_optmethod_trace (MethodTest):
    """
    Proxy must implement or reject TRACE method.
    """

    def test_optmethod_trace (self):
        self.start_test()

    def get_request_method (self):
        return "TRACE"


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
