# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""
import unittest, random
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY


class TestReplacer (unittest.TestCase):
    def setUp (self):
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
    unittest.main()
