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
Test end-to-end and unrecognized headers
"""

from tests import make_suite
from wc.proxy.tests import ProxyTest

class test_endhdr_fwd_atom_Expect_100_continue_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued Expect: 100-continue request header.
    """

    def test_endhdr_fwd_atom_Expect_100_continue_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_Expect_100_continue_toSrv, self).get_request_headers(content)
        headers.append("Expect: 100-continue")
        return headers

    def check_request_headers (self, request):
        self.assert_(request.has_header("Expect"))
        self.assertEqual(request.get_header("Expect"), "100-continue")


class test_endhdr_fwd_atom_Server_comm_no_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued Server: response header without
    comment.
    """

    def test_endhdr_fwd_atom_Server_comm_no_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_Server_comm_no_toClt, self).get_response_headers(content)
        headers.append("Server: foo")
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("Server"))
        self.assertEqual(response.get_header("Server"), "foo")


class test_endhdr_fwd_atom_Server_comm_plain_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued Server: response header with plain
    comment.
    """

    def test_endhdr_fwd_atom_Server_comm_plain_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_Server_comm_plain_toClt, self).get_response_headers(content)
        headers.append("Server: (foo)")
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("Server"))
        self.assertEqual(response.get_header("Server"), "(foo)")


class test_endhdr_fwd_atom_xtension_value_plain_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued extension response header with plain
    value.
    """

    def test_endhdr_fwd_atom_xtension_value_plain_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_plain_toClt, self).get_response_headers(content)
        headers.append("Wummel: bummel")
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("Wummel"))
        self.assertEqual(response.get_header("Wummel"), "bummel")


class test_endhdr_fwd_atom_xtension_value_plain_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued extension request header with plain
    value.
    """

    def test_endhdr_fwd_atom_xtension_value_plain_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_plain_toSrv, self).get_request_headers(content)
        headers.append("Wummel: bummel")
        return headers

    def check_request_headers (self, request):
        self.assert_(request.has_header("Wummel"))
        self.assertEqual(request.get_header("Wummel"), "bummel")


class test_endhdr_fwd_atom_xtension_value_none_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued extension response header with no
    value.
    """

    def test_endhdr_fwd_atom_xtension_value_none_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_none_toClt, self).get_response_headers(content)
        headers.append("Wummel:")
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("Wummel"))
        self.assertEqual(response.get_header("Wummel"), "")


class test_endhdr_fwd_atom_xtension_value_none_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued extension request header with no
    value.
    """

    def test_endhdr_fwd_atom_xtension_value_none_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_none_toSrv, self).get_request_headers(content)
        headers.append("Wummel:")
        return headers

    def check_request_headers (self, request):
        self.assert_(request.has_header("Wummel"))
        self.assertEqual(request.get_header("Wummel"), "")


class test_endhdr_fwd_atom_xtension_value_long_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued extension response header with
    long value.
    """

    def test_endhdr_fwd_atom_xtension_value_long_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_long_toClt, self).get_response_headers(content)
        headers.append("Wummel: " + ("a" * 1024))
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("Wummel"))
        self.assertEqual(response.get_header("Wummel"), "a" * 1024)


class test_endhdr_fwd_atom_xtension_value_long_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued extension request header with
    long value.
    """

    def test_endhdr_fwd_atom_xtension_value_long_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_value_long_toSrv, self).get_request_headers(content)
        headers.append("Wummel: " + ("a" * 1024))
        return headers

    def check_request_headers (self, request):
        self.assert_(request.has_header("Wummel"))
        self.assertEqual(request.get_header("Wummel"), "a" * 1024)


class test_endhdr_fwd_atom_xtension_name_long_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued extension response header with
    long name.
    """

    def test_endhdr_fwd_atom_xtension_name_long_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_name_long_toClt, self).get_response_headers(content)
        name = "Wummel" + ("a" * 1024)
        headers.append(name + ": foo")
        return headers

    def check_response_headers (self, response):
        name = "Wummel" + ("a" * 1024)
        self.assert_(response.has_header(name))
        self.assertEqual(response.get_header(name), "foo")


class test_endhdr_fwd_atom_xtension_name_long_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued extension request header with
    long name.
    """

    def test_endhdr_fwd_atom_xtension_name_long_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = \
        super(test_endhdr_fwd_atom_xtension_name_long_toSrv, self).get_request_headers(content)
        name = "Wummel" + ("a" * 1024)
        headers.append(name + ": foo")
        return headers

    def check_request_headers (self, request):
        name = "Wummel" + ("a" * 1024)
        self.assert_(request.has_header(name))
        self.assertEqual(request.get_header(name), "foo")


class test_endhdr_fwd_atom_xtension_name_dot_toClt (ProxyTest):
    """
    Proxy MUST forward single-valued extension response header named
    dot.
    """

    def test_endhdr_fwd_atom_xtension_name_dot_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        headers = super(test_endhdr_fwd_atom_xtension_name_dot_toClt, self).get_response_headers(content)
        headers.append(".: foo")
        return headers

    def check_response_headers (self, response):
        self.assert_(response.has_header("."))
        self.assertEqual(response.get_header("."), "foo")


class test_endhdr_fwd_atom_xtension_name_dot_toSrv (ProxyTest):
    """
    Proxy MUST forward single-valued extension request header named
    dot.
    """

    def test_endhdr_fwd_atom_xtension_name_dot_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = super(test_endhdr_fwd_atom_xtension_name_dot_toSrv, self).get_request_headers(content)
        headers.append(".: foo")
        return headers

    def check_request_headers (self, request):
        self.assert_(request.has_header("."))
        self.assertEqual(request.get_header("."), "foo")


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
