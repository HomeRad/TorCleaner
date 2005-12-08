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
Test leading zeros in HTTP version
"""

from wc.proxy.ftests import ProxyTest, make_suite


class test_lead0s_major_toSrv (ProxyTest):
    """
    Leading zeros in major version number.
    """

    def test_lead0s_major_toSrv (self):
        self.start_test()

    def construct_request_data (self, request):
        # construct HTTP request
        lines = []
        version = "00%d.%d" % request.version
        lines.append("%s %s HTTP/%s" % (request.method, request.uri, version))
        lines.extend(request.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if request.content:
            data += request.content
        return data


class test_lead0s_minor_toSrv (ProxyTest):
    """
    Leading zeros in minor version number.
    """

    def test_lead0s_minor_toSrv (self):
        self.start_test()

    def construct_request_data (self, request):
        # construct HTTP request
        lines = []
        version = "%d.00%d" % request.version
        lines.append("%s %s HTTP/%s" % (request.method, request.uri, version))
        lines.extend(request.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if request.content:
            data += request.content
        return data


class test_lead0s_major_toClt (ProxyTest):
    """
    Leading zeros in major version number.
    """

    def test_lead0s_major_toClt (self):
        self.start_test()

    def construct_response_data (self, response):
        lines = []
        version = "00%d.%d" % response.version
        lines.append("HTTP/%s %d %s" % (version, response.status, response.msg))
        lines.append("Content-Type: text/plain")
        lines.append("Content-Length: %d" % len(response.content))
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if response.content:
            data += response.content
        return data


class test_lead0s_minor_toClt (ProxyTest):
    """
    Leading zeros in minor version number.
    """

    def test_lead0s_minor_toClt (self):
        self.start_test()

    def construct_response_data (self, response):
        lines = []
        version = "%d.00%d" % response.version
        lines.append("HTTP/%s %d %s" % (version, response.status, response.msg))
        lines.append("Content-Type: text/plain")
        lines.append("Content-Length: %d" % len(response.content))
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if response.content:
            data += response.content
        return data


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
