#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest

import wc
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST

class TestBlocker (unittest.TestCase):

    def setUp (self):
        self.url = "http://ads.realmedia.com/"
        wc.configuration.config = wc.configuration.Configuration()
        wc.configuration.config['filters'] = ['Blocker',]
        wc.configuration.config.init_filter_modules()

    def test_block (self):
        data = "GET %s HTTP/1.0" % self.url
        attrs = get_filterattrs(self.url, [FILTER_REQUEST])
        filtered = applyfilter(FILTER_REQUEST, data, 'finish', attrs)
        self.assert_(filtered.find("blocked.html")!=-1)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBlocker))
    return suite

if __name__ == '__main__':
    unittest.main()
