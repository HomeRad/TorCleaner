# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""
import unittest, random, os
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from tests import StandardTest

class TestReplacer (StandardTest):

    def init (self):
        super(TestReplacer, self).init()
        wc.config = wc.Configuration()
        wc.config['filters'] = ['Replacer']
        wc.config.init_filter_modules()

    def testReplaceRandom (self):
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
        # filter random data, should not raise any exception
        data = []
        for i in range(1024):
            data.append(chr(random.randint(0, 255)))
        data = "".join(data)
        applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)


if __name__ == '__main__':
    unittest.main(defaultTest='TestReplacer')
else:
    suite = unittest.makeSuite(TestReplacer, 'test')
