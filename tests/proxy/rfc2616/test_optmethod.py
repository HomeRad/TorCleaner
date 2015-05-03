# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam
"""
Test optional methods.
"""

from .. import ProxyTest


class MethodTest(ProxyTest):

    def check_response_status(self, response):
        self.assertTrue(response.status in (405, 200))

    def check_response_message(self, response):
        pass

    def check_response_method(self, response):
        if response.status == 200:
            self.check_response_method2(response)

    def check_response_method2(self, response):
        pass

    def check_response_content(self, response):
        if response.status == 200:
            self.assertEqual(response.content, self.get_response_content())


class test_optmethod_options(MethodTest):
    """
    Proxy must implement or reject OPTIONS method.
    """

    def test_optmethod_options(self):
        self.start_test()

    def get_request_method(self):
        return "OPTIONS"

    def check_response_method2(self, response):
        if response.content:
            # Content-Type must be included
            self.assertTrue(response.has_header("Content-Type"))
        else:
            self.assertTrue(response.has_header("Content-Length"))
            self.assertEqual(response.get_header("Content-Length"), "0")


class test_optmethod_trace(MethodTest):
    """
    Proxy must implement or reject TRACE method.
    """

    def test_optmethod_trace(self):
        self.start_test()

    def get_request_method(self):
        return "TRACE"
