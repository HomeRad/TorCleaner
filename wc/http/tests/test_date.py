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
import wc.http.date
from wc.tests import MsgTestCase


class TestDate (MsgTestCase):

    def test_rfc1123 (self):
        now = time.time()
        d = wc.http.date.get_date_rfc1123(now)
        s = "Sat, 12 Feb 0005 11:12:13 GMT"
        t = (0005, 2, 12, 11, 12, 13, 5, 43, 0)
        self.assertEquals(wc.http.date.parse_date_rfc1123(s), t)
        s = "Sat, 01 Nov 2099 01:02:03 GMT"
        t = (2099, 11, 1, 1, 2, 3, 5, 305, 0)
        self.assertEquals(wc.http.date.parse_date_rfc1123(s), t)
        s = "Tue, 99 Feb 2000 12:13:14 GMT"
        self.assertRaises(ValueError, wc.http.date.parse_date_rfc1123, s)

    def test_rfc850 (self):
        now = time.time()
        d = wc.http.date.get_date_rfc850(now)
        s = "Saturday, 12-Feb-09 11:12:13 GMT"
        t = (2009, 2, 12, 11, 12, 13, 5, 43, 0)
        self.assertEquals(wc.http.date.parse_date_rfc850(s), t)
        s = "Saturday, 01-Nov-05 01:02:03 GMT"
        t = (2005, 11, 1, 1, 2, 3, 5, 305, 0)
        self.assertEquals(wc.http.date.parse_date_rfc850(s), t)
        s = "Tuesday, 99-Feb-98 12:13:14 GMT"
        self.assertRaises(ValueError, wc.http.date.parse_date_rfc850, s)

    def test_asctime (self):
        now = time.time()
        d = wc.http.date.get_date_asctime(now)
        s = "Sat Feb 12 11:12:13 2005"
        t = (2005, 2, 12, 11, 12, 13, 5, 43, 0)
        self.assertEquals(wc.http.date.parse_date_asctime(s), t)
        s = "Sat Nov  1 01:02:03 2099"
        t = (2099, 11, 1, 1, 2, 3, 5, 305, 0)
        self.assertEquals(wc.http.date.parse_date_asctime(s), t)
        s = "Tue Feb 99 12:13:14 2000"
        self.assertRaises(ValueError, wc.http.date.parse_date_asctime, s)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    return unittest.makeSuite(TestDate)
