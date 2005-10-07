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
"""
"""

import time
from wc.proxy.ftests import ProxyTest, make_suite
from wc.http.date import get_date_rfc850, get_date_rfc1123, get_date_asctime

class test_dateformat_warn_rfc1123_rfc850 (ProxyTest):
    """
    Test deletion of Warning: header with rfc850 date and
    Date: header with rfc1123 date.
    """

    def test_dateformat_warn_rfc1123_rfc850 (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_rfc850(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_dateformat_warn_rfc1123_asctime (ProxyTest):
    """
    Test deletion of Warning: header with asctime date and
    Date: header with rfc1123 date.
    """

    def test_dateformat_warn_rfc1123_asctime (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_asctime(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc1123(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_dateformat_warn_rfc850_rfc1123 (ProxyTest):
    """
    Test deletion of Warning: header with rfc1123 date and
    Date: header with rfc850 date.
    """

    def test_dateformat_warn_rfc850_rfc1123 (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_rfc1123(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc850(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_dateformat_warn_rfc850_asctime (ProxyTest):
    """
    Test deletion of Warning: header with asctime date and
    Date: header with rfc850 date.
    """

    def test_dateformat_warn_rfc850_asctime (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_asctime(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_rfc850(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_dateformat_warn_asctime_rfc1123 (ProxyTest):
    """
    Test deletion of Warning: header with rfc1123 date and
    Date: header with asctime date.
    """

    def test_dateformat_warn_asctime_rfc1123 (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_rfc1123(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_asctime(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_dateformat_warn_asctime_rfc850 (ProxyTest):
    """
    Test deletion of Warning: header with rfc850 date and
    Date: header with asctime date.
    """

    def test_dateformat_warn_asctime_rfc850 (self):
        self.start_test()

    def get_response_headers (self, content):
        now = time.time()
        warndate = get_date_rfc850(now - 5)
        warning = '119 smee "hulla" "%s"' % warndate
        date = get_date_asctime(now)
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
            "Warning: %s" % warning,
            "Date: %s" % date,
        ]

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())

