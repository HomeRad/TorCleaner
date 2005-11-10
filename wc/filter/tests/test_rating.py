# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Test rating routines.
"""

import unittest

import wc.filter.rating
import wc.filter.rating.category
from wc.tests import MsgTestCase


class TestRating (MsgTestCase):

    def test_split_url (self):
        """
        Test url splitting.
        """
        urls = (
            ('', []),
            ('a', []),
            ('a/b', []),
            ('http://imadoofus.com', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com//', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/?q=a', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/?q=a#a', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/a/b//c', ['http://', 'imadoofus.com', '/', 'a', '/', 'b', '/', 'c']),
            ('http://imadoofus.com/forum', ['http://', 'imadoofus.com', '/', 'forum']),
            ('http://imadoofus.com/forum/', ['http://', 'imadoofus.com', '/', 'forum']),
        )
        for url, res in urls:
            self.assertEqual(wc.filter.rating.split_url(url), res)

    def test_range_range (self):
        """
        Test range in range.
        """
        in_range = wc.filter.rating.category.range_in_range
        # in_range(vrange, prange)
        self.assert_(in_range((1, 1), (None, None)))
        self.assert_(in_range((None, None), (1, 1)))
        self.assert_(in_range((1, None), (None, 1)))
        self.assert_(in_range((None, 1), (1, None)))
        self.assert_(in_range((1, 2), (1, 2)))
        self.assert_(not in_range((0, 1), (1, 2)))
        self.assert_(not in_range((1, 3), (1, 2)))
        self.assert_(not in_range((0, None), (1, 2)))
        self.assert_(not in_range((None, 3), (1, 2)))
        self.assert_(not in_range((1, 3), (4, 7)))

    def test_range_value (self):
        """
        Test value in range.
        """
        in_range = wc.filter.rating.category.value_in_range
        # in_range(value, prange)
        self.assert_(in_range(1, (None, None)))
        self.assert_(in_range(None, (1, 1)))
        self.assert_(in_range(None, (None, 1)))
        self.assert_(in_range(1, (None, 1)))
        self.assert_(in_range(None, (1, None)))
        self.assert_(in_range(1, (1, None)))
        self.assert_(in_range(1, (1, 2)))
        self.assert_(in_range(2, (1, 2)))
        self.assert_(not in_range(0, (1, 2)))
        self.assert_(not in_range(3, (1, 2)))
        self.assert_(not in_range(1, (4, 7)))

    def test_rating_range (self):
        """
        Test range parsing.
        """
        # rating_range (range)
        rating_range = wc.filter.rating.category.intrange_from_string
        self.assertEqual(rating_range(""), (None, None))
        self.assertEqual(rating_range("-"), (None, None))
        self.assertEqual(rating_range("1"), (1, None))
        self.assertEqual(rating_range("1-"), (1, None))
        self.assertEqual(rating_range("-1"), (None, 1))
        self.assertEqual(rating_range("1-1"), (1, 1))
        self.assertEqual(rating_range("-1-"), None)


def test_suite ():
    return unittest.makeSuite(TestRating)

if __name__ == '__main__':
    unittest.main()
