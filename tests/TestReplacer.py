# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""
import unittest, random, os
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.log import initlog


class TestReplacer (unittest.TestCase):
    def setUp (self):
        wc.config = wc.Configuration()
        wc.config['filters'] = ['Replacer']
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))


    def testReplaceRandom (self):
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
        # filter random data, should not raise any exception
        data = []
        for i in range(1024):
            data.append(chr(random.randint(0, 255)))
        data = "".join(data)
        applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)


suite = unittest.makeSuite(TestReplacer,'test')

if __name__ == '__main__':
    unittest.main()
