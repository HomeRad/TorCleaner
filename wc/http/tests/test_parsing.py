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

import unittest
import time
import wc.http
import wc.http.date
from wc.tests import MsgTestCase


class TestBasic (MsgTestCase):

    def test_http_version (self):
        self.assertEquals(wc.http.parse_http_version("HTTP/0.0"), (0, 0))
        self.assertEquals(wc.http.parse_http_version("foo"), (2, 0))
        self.assertEquals(wc.http.parse_http_version("HTTP/01.1"), (1, 1))
        self.assertEquals(wc.http.parse_http_version("HTtP/1.01"), (1, 1))
        self.assertEquals(wc.http.parse_http_version("HTTP/-1.1"), (2, 0))

    def test_request (self):
        request = "GET / HTTP/1.1"
        parsed = ("GET", "/", (1, 1))
        self.assertEquals(wc.http.parse_http_request(request), parsed)
        request = "GET  /  HTTP/1.1"
        parsed = ("GET", "/", (1, 1))
        self.assertEquals(wc.http.parse_http_request(request), parsed)
        request = " GET  /  HTTP/1.1 "
        parsed = ("GET", "/", (1, 1))
        self.assertEquals(wc.http.parse_http_request(request), parsed)

    def test_response (self):
        response = "HTTP/1.1 200 foo"
        url = "unknown"
        parsed = [(1, 1), 200, "foo"]
        self.assertEquals(wc.http.parse_http_response(response, url), parsed)
        response = "HTTP/1.1 -200 foo"
        parsed = [(1, 1), 200, "foo"]
        self.assertEquals(wc.http.parse_http_response(response, url), parsed)
        response = "HTTP/1.1 999 glork bla"
        parsed = [(1, 1), 200, "glork bla"]
        self.assertEquals(wc.http.parse_http_response(response, url), parsed)

    def test_quoted_string (self):
        s = '"a b c d"  foo bla'
        self.assertEquals(wc.http.split_quoted_string(s),
                          ('a b c d', 'foo bla'))
        s = r'"a b\" \\ \a\b\ c d" foo bla'
        self.assertEquals(wc.http.split_quoted_string(s),
                          (r'a b" \ ab c d', 'foo bla'))
        s = "'a' b"
        self.assertRaises(ValueError, wc.http.split_quoted_string, s)

    def test_warning (self):
        now = time.time()
        date = wc.http.date.get_date_rfc1123(now)
        datewarn= '119 smee "hulla" "%s"' % date
        warn = '119 smee "wulla"'
        self.assertEquals(wc.http.parse_http_warning(warn),
                          (119, "smee", "wulla", None))
        self.assertEquals(wc.http.parse_http_warning(datewarn),
                          (119, "smee", "hulla", time.gmtime(now)))


def test_suite ():
    """
    Build and return a TestSuite.
    """
    return unittest.makeSuite(TestBasic)
