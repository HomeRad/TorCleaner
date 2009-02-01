# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
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
import wc.rating.service.ratingformat


class TestRating (unittest.TestCase):

    def test_range_range (self):
        """Test range in range."""
        range_c = wc.rating.service.ratingformat.IntRange
        self.assert_(range_c(1, 1).contains_range(range_c()))
        self.assert_(range_c().contains_range(range_c(1, 1)))
        self.assert_(range_c(1, None).contains_range(range_c(None, 1)))
        self.assert_(range_c(None, 1).contains_range(range_c(1)))
        self.assert_(range_c(1, 2).contains_range(range_c(1, 2)))
        self.assert_(not range_c(0, 1).contains_range(range_c(1, 2)))
        self.assert_(not range_c(1, 2).contains_range(range_c(1, 3)))
        self.assert_(not range_c(1, 2).contains_range(range_c(0)))
        self.assert_(not range_c(1, 2).contains_range(range_c(None, 3)))
        self.assert_(not range_c(1, 3).contains_range(range_c(4, 7)))

    def test_range_value (self):
        """Test value in range."""
        range_c = wc.rating.service.ratingformat.IntRange
        self.assert_(range_c().contains_value(1))
        self.assert_(range_c(1, 1).contains_value(None))
        self.assert_(range_c(None, 1).contains_value(None))
        self.assert_(range_c(None, 1).contains_value(1))
        self.assert_(range_c(1, None).contains_value(None))
        self.assert_(range_c(1, None).contains_value(1))
        self.assert_(range_c(1, 2).contains_value(1))
        self.assert_(range_c(1, 2).contains_value(2))
        self.assert_(not range_c(1, 2).contains_value(0))
        self.assert_(not range_c(1, 2).contains_value(3))
        self.assert_(not range_c(4, 7).contains_value(1))

    def test_rating_range (self):
        """Test range parsing."""
        # rating_range (range)
        parse_range = wc.rating.service.ratingformat.parse_range
        range_c = wc.rating.service.ratingformat.IntRange
        self.assertEqual(parse_range(""), range_c())
        self.assertEqual(parse_range("-"), range_c())
        self.assertEqual(parse_range("1"), range_c(1))
        self.assertEqual(parse_range("1-"), range_c(1))
        self.assertEqual(parse_range("-1"), range_c(None, 1))
        self.assertEqual(parse_range("1-1"), range_c(1, 1))
        self.assertEqual(parse_range("-1-"), None)
