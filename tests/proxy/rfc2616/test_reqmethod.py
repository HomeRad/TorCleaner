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
Test required methods.
"""

from tests import make_suite
from .. import ProxyTest


class test_reqmethod_head (ProxyTest):
    """
    Proxy must support HEAD request.
    """

    def test_reqmethod_head (self):
        self.start_test()

    def get_request_method (self):
        return "HEAD"

    def check_response_content (self, response):
        self.assert_(not response.content)


class test_reqmethod_get (ProxyTest):
    """
    Proxy must support GET request.
    """

    def test_reqmethod_get (self):
        self.start_test()


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
