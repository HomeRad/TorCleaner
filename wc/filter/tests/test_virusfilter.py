# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest
import wc
import wc.proxy.Headers
import wc.filter


class TestVirusFilter (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def init (self):
        super(TestVirusFilter, self).init()
        wc.config = wc.Configuration()
        wc.config['filters'] = ['VirusFilter']
        wc.config.init_filter_modules()
        wc.filter.VirusFilter.init_clamav_conf()

    def setUp (self):
        headers = wc.proxy.Headers.WcMessage()
        headers['Content-Type'] = "text/html"
        self.attrs = wc.filter.get_filterattrs("", [wc.filter.FILTER_RESPONSE_MODIFY], headers=headers)

    def filt (self, data, result):
        filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'finish', self.attrs)
        self.assertEqual(filtered, result)

    def filtSize (self, size):
        i = 0L
        inc = 10000
        data = 'a'*inc
        while i <= size:
            wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'filter', self.attrs)
            i += inc
        wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, "finish", self.attrs)

    def testBasic (self):
        self.filt("""Test""", """Test""")

    def testTestSignature (self):
        self.filt("""$CEliacmaTrESTuScikgsn$FREE-TEST-SIGNATURE$EEEEE$""",
                  "")

    def testSizeLimit (self):
        size = wc.filter.VirusFilter.VirusFilter.MAX_FILE_BYTES+1
        self.assertRaises(wc.filter.FilterProxyError, self.filtSize, size)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestVirusFilter))
    return suite

if __name__ == '__main__':
    unittest.main()

