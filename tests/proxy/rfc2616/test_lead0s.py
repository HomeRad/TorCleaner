# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test leading zeros in HTTP version
"""

from .. import ProxyTest


class test_lead0s_major_toSrv(ProxyTest):
    """
    Leading zeros in major version number.
    """

    def test_lead0s_major_toSrv(self):
        self.start_test()

    def construct_request_data(self, request):
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


class test_lead0s_minor_toSrv(ProxyTest):
    """
    Leading zeros in minor version number.
    """

    def test_lead0s_minor_toSrv(self):
        self.start_test()

    def construct_request_data(self, request):
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


class test_lead0s_major_toClt(ProxyTest):
    """
    Leading zeros in major version number.
    """

    def test_lead0s_major_toClt(self):
        self.start_test()

    def construct_response_data(self, response):
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


class test_lead0s_minor_toClt(ProxyTest):
    """
    Leading zeros in minor version number.
    """

    def test_lead0s_minor_toClt(self):
        self.start_test()

    def construct_response_data(self, response):
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
