# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""
import unittest
import random

import wc
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY


class TestReplacer (unittest.TestCase):

    def init (self):
        super(TestReplacer, self).init()
        wc.configuration.config = wc.configuration.Configuration()
        wc.configuration.config['filters'] = ['Replacer']
        wc.configuration.config.init_filter_modules()

    def testReplaceRandom (self):
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
        # filter random data, should not raise any exception
        data = []
        for dummy in range(1024):
            data.append(chr(random.randint(0, 255)))
        data = "".join(data)
        applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)

    def testReplaceNonAscii (self):
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
        data = "äöü asdfö"
        applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReplacer))
    return suite

if __name__ == '__main__':
    unittest.main()
