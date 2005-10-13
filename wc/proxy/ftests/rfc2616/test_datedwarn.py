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
from wc.http.date import get_date_rfc1123


class test_datedwarn_1old_0cur_0fut (ProxyTest):

    def test_datedwarn_1old_0cur_0fut (self):
        self.start_test()

    def get_response_headers (self, content):
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

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_datedwarn_0old_0cur_1fut (ProxyTest):

    def test_datedwarn_0old_0cur_1fut (self):
        self.start_test()

    def get_response_headers (self, content):
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

    def check_response_headers (self, response):
        self.assert_(not response.has_header("Warning"))


class test_datedwarn_1old_1cur_1fut (ProxyTest):

    def test_datedwarn_1old_1cur_1fut (self):
        self.start_test()

    def get_response_headers (self, content):
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

    def check_response_headers (self, response):
        self.assertEquals(response.num_headers('Warning'), 1)


class test_datedwarn_1old_continuation (ProxyTest):

    def test_datedwarn_1old_continuation (self):
        self.start_test()

    def get_response_headers (self, content):
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

    def check_response_headers (self, response):
        self.assert_(not response.has_header('Warning'))


class test_datedwarn_1cur_continuation (ProxyTest):

    def test_datedwarn_1cur_continuation (self):
        self.start_test()

    def get_response_headers (self, content):
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

    def check_response_headers (self, response):
        self.assertEquals(response.num_headers('Warning'), 1)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())
