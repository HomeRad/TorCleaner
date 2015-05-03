# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam
"""
Test hop-by-hop headers
"""

from .. import ProxyTest

class test_hophdr_connection_toSrv(ProxyTest):
    """
    Proxy must not forward Connection: request header
    """

    def test_hophdr_connection_toSrv(self):
        self.start_test()

    def get_request_headers(self, content):
        headers = \
        super(test_hophdr_connection_toSrv, self).get_request_headers(content)
        headers.append("Connection: foo")
        return headers

    def check_request_headers(self, request):
        if request.has_header("Connection"):
            self.assertNotEqual(request.get_header("Connection"), "foo")


class test_hophdr_keepalive_toSrv(ProxyTest):
    """
    Proxy must not forward Keep-Alive: request header
    """

    def test_hophdr_keepalive_toSrv(self):
        self.start_test()

    def get_request_headers(self, content):
        headers = \
        super(test_hophdr_keepalive_toSrv, self).get_request_headers(content)
        headers.append("Keep-Alive: foo")
        return headers

    def check_request_headers(self, request):
        if request.has_header("Keep-Alive"):
            self.assertNotEqual(request.get_header("Keep-Alive"), "foo")


class test_hophdr_upgrade_toSrv(ProxyTest):
    """
    Proxy must not forward Upgrade: request header
    """

    def test_hophdr_upgrade_toSrv(self):
        self.start_test()

    def get_request_headers(self, content):
        headers = \
        super(test_hophdr_upgrade_toSrv, self).get_request_headers(content)
        headers.append("Upgrade: foo")
        return headers

    def check_request_headers(self, request):
        if request.has_header("Upgrade"):
            self.assertNotEqual(request.get_header("Upgrade"), "foo")


class test_hophdr_trailer_toSrv(ProxyTest):
    """
    Proxy must not forward Trailer: request header
    """

    def test_hophdr_trailer_toSrv(self):
        self.start_test()

    def get_request_headers(self, content):
        headers = \
        super(test_hophdr_trailer_toSrv, self).get_request_headers(content)
        headers.append("Trailer: foo")
        return headers

    def check_request_headers(self, request):
        if request.has_header("Trailer"):
            self.assertNotEqual(request.get_header("Trailer"), "foo")


class test_hophdr_te_toSrv(ProxyTest):
    """
    Proxy must not forward TE: request header
    """

    def test_hophdr_te_toSrv(self):
        self.start_test()

    def get_request_headers(self, content):
        headers = \
        super(test_hophdr_te_toSrv, self).get_request_headers(content)
        headers.append("TE: foo")
        return headers

    def check_request_headers(self, request):
        if request.has_header("TE"):
            self.assertNotEqual(request.get_header("TE"), "foo")


class test_hophdr_connection_toClt(ProxyTest):
    """
    Proxy must not forward Connection: response header
    """

    def test_hophdr_connection_toClt(self):
        self.start_test()

    def get_response_headers(self, content):
        headers = \
        super(test_hophdr_connection_toClt, self).get_response_headers(content)
        headers.append("Connection: foo")
        return headers

    def check_response_headers(self, response):
        if response.has_header("Connection"):
            self.assertNotEqual(response.get_header("Connection"), "foo")


class test_hophdr_keepalive_toClt(ProxyTest):
    """
    Proxy must not forward Keep-Alive: response header
    """

    def test_hophdr_keepalive_toClt(self):
        self.start_test()

    def get_response_headers(self, content):
        headers = \
        super(test_hophdr_keepalive_toClt, self).get_response_headers(content)
        headers.append("Keep-Alive: foo")
        return headers

    def check_response_headers(self, response):
        if response.has_header("Keep-Alive"):
            self.assertNotEqual(response.get_header("Keep-Alive"), "foo")


class test_hophdr_upgrade_toClt(ProxyTest):
    """
    Proxy must not forward Upgrade: response header
    """

    def test_hophdr_upgrade_toClt(self):
        self.start_test()

    def get_response_headers(self, content):
        headers = \
        super(test_hophdr_upgrade_toClt, self).get_response_headers(content)
        headers.append("Upgrade: foo")
        return headers

    def check_response_headers(self, response):
        if response.has_header("Upgrade"):
            self.assertNotEqual(response.get_header("Upgrade"), "foo")


class test_hophdr_trailer_toClt(ProxyTest):
    """
    Proxy must not forward Trailer: response header
    """

    def test_hophdr_trailer_toClt(self):
        self.start_test()

    def get_response_headers(self, content):
        headers = \
        super(test_hophdr_trailer_toClt, self).get_response_headers(content)
        headers.append("Trailer: foo")
        return headers

    def check_response_headers(self, response):
        if response.has_header("Trailer"):
            self.assertNotEqual(response.get_header("Trailer"), "foo")


class test_hophdr_proxyauth_toClt(ProxyTest):
    """
    Proxy must not forward Proxy-Authenticate: response header
    """

    def test_hophdr_proxyauth_toClt(self):
        self.start_test()

    def get_response_headers(self, content):
        headers = \
        super(test_hophdr_proxyauth_toClt, self).get_response_headers(content)
        headers.append("Proxy-Authenticate: foo")
        return headers

    def check_response_headers(self, response):
        self.assertTrue(not response.has_header("Proxy-Authenticate"))
