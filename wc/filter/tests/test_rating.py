# -*- coding: iso-8859-1 -*-
"""test rating routines"""

import unittest
#from wc.filter.Rating import *


class TestRating (unittest.TestCase):

    def XXXtestRating_split_url (self):
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
            self.assertEqual(rating_split_url(url), res)

    def XXXtestRating_in_range (self):
        # rating_in_range (prange, value)
        self.assert_(rating_in_range((None, None), (1, 1)))
        self.assert_(rating_in_range((1, 1), (None, None)))
        self.assert_(rating_in_range((None, 1), (1, None)))
        self.assert_(rating_in_range((1, None), (None, 1)))
        self.assert_(rating_in_range((1, 2), (1, 2)))
        self.assert_(not rating_in_range((1, 2), (0, 1)))
        self.assert_(not rating_in_range((1, 2), (1, 3)))
        self.assert_(not rating_in_range((1, 2), (0, None)))
        self.assert_(not rating_in_range((1, 2), (None, 3)))

    def XXXtestRating_range (self):
        # rating_range (range)
        self.assertEqual(rating_range("-"), (None, None))
        self.assertEqual(rating_range("1-"), (1, None))
        self.assertEqual(rating_range("-1"), (None, 1))
        self.assertEqual(rating_range("1-1"), (1, 1))
        self.assertEqual(rating_range(""), None)
        self.assertEqual(rating_range("1"), None)
        self.assertEqual(rating_range("-1-"), None)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRating))
    return suite

if __name__ == '__main__':
    unittest.main()
