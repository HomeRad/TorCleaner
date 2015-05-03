# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2010 Bastian Kleineidam
"""
"""

import time
from .. import ProxyTest
from wc.http.date import get_date_rfc1123


class test_datedwarn_1old_0cur_0fut(ProxyTest):

    def test_datedwarn_1old_0cur_0fut(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        warndate = get_date_rfc1123(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertTrue(not response.has_header("Warning"))


class test_datedwarn_0old_0cur_1fut(ProxyTest):

    def test_datedwarn_0old_0cur_1fut(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        warndate = get_date_rfc1123(now + 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertTrue(not response.has_header("Warning"))


class test_datedwarn_1old_1cur_1fut(ProxyTest):

    def test_datedwarn_1old_1cur_1fut(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        futdate = get_date_rfc1123(now + 5)
        olddate = get_date_rfc1123(now - 5)
        futwarn= '119 smee "hulla" "%s"' % futdate
        oldwarn = '119 smee "bulla" "%s"' % olddate
        warn = '119 smee "wulla"'
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % oldwarn,
            "Warning: %s" % futwarn,
            "Warning: %s" % warn,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertEqual(response.num_headers('Warning'), 1)


class test_datedwarn_1old_continuation(ProxyTest):

    def test_datedwarn_1old_continuation(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        olddate = get_date_rfc1123(now - 5)
        oldwarn1 = '119 smee '
        oldwarn2 = '"bulla" "%s"' % olddate
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % oldwarn1,
            " %s" % oldwarn2,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertTrue(not response.has_header('Warning'))


class test_datedwarn_1cur_continuation(ProxyTest):

    def test_datedwarn_1cur_continuation(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        date = get_date_rfc1123(now)
        warn1 = '119 smee '
        warn2 = '"bulla" "%s"' % date
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warn1,
            " %s" % warn2,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertEqual(response.num_headers('Warning'), 1)


class test_datedwarn_1cur_noquotes(ProxyTest):

    def test_datedwarn_1cur_noquotes(self):
        self.start_test()

    def get_response_headers(self, content):
        now = time.time()
        date = get_date_rfc1123(now)
        warn = '110 DataReactor "Response is stale" %s' % date
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warn,
            "Date: %s" % date,
        ]

    def check_response_headers(self, response):
        self.assertEqual(response.num_headers('Warning'), 1)
