# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
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
Test localhost detection.
"""

from wc.proxy.tests import ProxyTest, make_suite

class LoopTest (ProxyTest):

    def get_hostname (self):
        # override in subclass
        pass

    def get_request_uri (self):
        return "http://%s:8081/" % self.get_hostname()

    def get_request_headers (self, content):
        headers = [
           "Host: %s:8081" % self.get_hostname(),
           "Proxy-Connection: close",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def check_response_content (self, response):
        # since proxy answers with config web interface, don't check here
        pass


class test_reqloop_loopip (LoopTest):
    """
    Proxy must detect that 127.0.0.1 is itself.
    """

    def test_reqloop_loopip (self):
        self.start_test()

    def get_hostname (self):
        return "127.0.0.1"


class test_reqloop_loopname (LoopTest):
    """
    Proxy must detect that localhost is itself.
    """

    def test_reqloop_loopname (self):
        self.start_test()

    def get_hostname (self):
        return "localhost"


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
