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
Test spell checker.
"""

import unittest
from wc.filter.html import check_spelling
from wc.tests import MsgTestCase


class TestSpelling (MsgTestCase):

    def test_htmltags (self):
        url = "unknown"
        self.assertEqual("blink", check_spelling("blink", url))
        self.assertEqual("blink", check_spelling("bllnk", url))
        self.assertEqual("html", check_spelling("htmm", url))
        self.assertEqual("hr", check_spelling("hrr", url))
        self.assertEqual("xmlns:a", check_spelling("xmlns:a", url))
        self.assertEqual("heisead", check_spelling("heisead", url))


def test_suite ():
    return unittest.makeSuite(TestSpelling)

if __name__ == '__main__':
    unittest.main()
