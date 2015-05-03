# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test spell checker.
"""

import unittest
from wc.filter.html import check_spelling


class TestSpelling(unittest.TestCase):

    def test_htmltags(self):
        url = "unknown"
        self.assertEqual("blink", check_spelling("blink", url))
        self.assertEqual("blink", check_spelling("bllnk", url))
        self.assertEqual("html", check_spelling("htmm", url))
        self.assertEqual("hr", check_spelling("hrr", url))
        self.assertEqual("xmlns:a", check_spelling("xmlns:a", url))
        self.assertEqual("heisead", check_spelling("heisead", url))
