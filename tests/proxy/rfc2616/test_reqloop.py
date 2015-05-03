# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test localhost detection.
"""

from .. import ProxyTest


class LoopTest(ProxyTest):

    def get_hostname(self):
        # override in subclass
        pass

    def get_request_uri(self):
        return "http://%s:8081/" % self.get_hostname()

    def get_request_headers(self, content):
        headers = [
           "Host: %s:8081" % self.get_hostname(),
           "Proxy-Connection: close",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def check_response_content(self, response):
        # since proxy answers with config web interface, don't check here
        pass


class test_reqloop_loopip(LoopTest):
    """
    Proxy must detect that 127.0.0.1 is itself.
    """

    def test_reqloop_loopip(self):
        self.start_test()

    def get_hostname(self):
        return "127.0.0.1"


class test_reqloop_loopname(LoopTest):
    """
    Proxy must detect that localhost is itself.
    """

    def test_reqloop_loopname(self):
        self.start_test()

    def get_hostname(self):
        return "localhost"
