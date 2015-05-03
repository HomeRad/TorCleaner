# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam

import unittest
import time
import wc.http.date


class TestBasic(unittest.TestCase):

    def test_http_version(self):
        self.assertEqual(wc.http.parse_http_version("HTTP/0.0"), (0, 0))
        self.assertEqual(wc.http.parse_http_version("foo"), (2, 0))
        self.assertEqual(wc.http.parse_http_version("HTTP/01.1"), (1, 1))
        self.assertEqual(wc.http.parse_http_version("HTtP/1.01"), (1, 1))
        self.assertEqual(wc.http.parse_http_version("HTTP/-1.1"), (2, 0))

    def test_request(self):
        request = "GET / HTTP/1.1"
        parsed = ("GET", "/", (1, 1))
        self.assertEqual(wc.http.parse_http_request(request), parsed)
        request = "GET  /  HTTP/1.1"
        parsed = ("GET", "/", (1, 1))
        self.assertEqual(wc.http.parse_http_request(request), parsed)
        request = " GET  /  HTTP/1.1 "
        parsed = ("GET", "/", (1, 1))
        self.assertEqual(wc.http.parse_http_request(request), parsed)

    def test_response(self):
        response = "HTTP/1.1 200 foo"
        url = "unknown"
        parsed = [(1, 1), 200, "OK"]
        self.assertEqual(wc.http.parse_http_response(response, url), parsed)
        response = "HTTP/1.1 -200 foo"
        parsed = [(1, 1), 200, "OK"]
        self.assertEqual(wc.http.parse_http_response(response, url), parsed)
        response = "HTTP/1.1 999 glork bla"
        parsed = [(1, 1), 200, "OK"]
        self.assertEqual(wc.http.parse_http_response(response, url), parsed)

    def test_quoted_string(self):
        s = '"a b c d"  foo bla'
        self.assertEqual(wc.http.split_quoted_string(s),
                          ('a b c d', 'foo bla'))
        s = r'"a b\" \\ \a\b\ c d" foo bla'
        self.assertEqual(wc.http.split_quoted_string(s),
                          (r'a b" \ ab c d', 'foo bla'))
        s = "'a' b"
        self.assertRaises(ValueError, wc.http.split_quoted_string, s)

    def test_warning(self):
        now = time.time()
        date = wc.http.date.get_date_rfc1123(now)
        warn= '119 smee "hulla" "%s"' % date
        self.assertEqual(wc.http.parse_http_warning(warn),
                          (119, "smee", "hulla", time.gmtime(now)))
        warn = '119 smee "wulla"'
        self.assertEqual(wc.http.parse_http_warning(warn),
                          (119, "smee", "wulla", None))
        warn = '110 Response is stale'
        self.assertEqual(wc.http.parse_http_warning(warn),
                          (110, "", "Response is stale", None))
