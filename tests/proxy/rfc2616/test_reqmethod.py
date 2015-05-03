# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam
"""
Test required methods.
"""

from .. import ProxyTest


class test_reqmethod_head(ProxyTest):
    """
    Proxy must support HEAD request.
    """

    def test_reqmethod_head(self):
        self.start_test()

    def get_request_method(self):
        return "HEAD"

    def check_response_content(self, response):
        self.assertTrue(not response.content)


class test_reqmethod_get(ProxyTest):
    """
    Proxy must support GET request.
    """

    def test_reqmethod_get(self):
        self.start_test()
