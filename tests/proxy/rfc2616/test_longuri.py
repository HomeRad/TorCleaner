# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam
"""
Test long URIs.
"""

from .. import ProxyTest


class LonguriTest(ProxyTest):

    def longuri(self, bytes):
        octets = int(bytes / 8)
        remainder = max(0, (bytes % 8) - 1)
        return "/%s%s" % ("01234567" * octets, "x"*remainder)

    def check_response_status(self, response):
        self.assertTrue(response.status in (200, 414))


class test_longuri_1024(LonguriTest):
    """
    Test 1024 byte URI.
    """

    def test_longuri_1024(self):
        self.start_test()

    def get_request_uri(self):
        return self.longuri(1024)


class test_longuri_8192(LonguriTest):
    """
    Test 8192 byte URI.
    """

    def test_longuri_8192(self):
        self.start_test()

    def get_request_uri(self):
        return self.longuri(8192)


class test_longuri_65536(LonguriTest):
    """
    Test 65536 byte URI.
    """

    def test_longuri_65536(self):
        self.start_test()

    def get_request_uri(self):
        return self.longuri(65536)
