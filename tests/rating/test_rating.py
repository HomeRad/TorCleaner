# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010 Bastian Kleineidam
"""
Test rating routines.
"""

import unittest
import wc.rating.service.ratingformat


class TestRating(unittest.TestCase):

    def test_range_range(self):
        """Test range in range."""
        range_c = wc.rating.service.ratingformat.IntRange
        self.assertTrue(range_c(1, 1).contains_range(range_c()))
        self.assertTrue(range_c().contains_range(range_c(1, 1)))
        self.assertTrue(range_c(1, None).contains_range(range_c(None, 1)))
        self.assertTrue(range_c(None, 1).contains_range(range_c(1)))
        self.assertTrue(range_c(1, 2).contains_range(range_c(1, 2)))
        self.assertTrue(not range_c(0, 1).contains_range(range_c(1, 2)))
        self.assertTrue(not range_c(1, 2).contains_range(range_c(1, 3)))
        self.assertTrue(not range_c(1, 2).contains_range(range_c(0)))
        self.assertTrue(not range_c(1, 2).contains_range(range_c(None, 3)))
        self.assertTrue(not range_c(1, 3).contains_range(range_c(4, 7)))

    def test_range_value(self):
        """Test value in range."""
        range_c = wc.rating.service.ratingformat.IntRange
        self.assertTrue(range_c().contains_value(1))
        self.assertTrue(range_c(1, 1).contains_value(None))
        self.assertTrue(range_c(None, 1).contains_value(None))
        self.assertTrue(range_c(None, 1).contains_value(1))
        self.assertTrue(range_c(1, None).contains_value(None))
        self.assertTrue(range_c(1, None).contains_value(1))
        self.assertTrue(range_c(1, 2).contains_value(1))
        self.assertTrue(range_c(1, 2).contains_value(2))
        self.assertTrue(not range_c(1, 2).contains_value(0))
        self.assertTrue(not range_c(1, 2).contains_value(3))
        self.assertTrue(not range_c(4, 7).contains_value(1))

    def test_rating_range(self):
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
