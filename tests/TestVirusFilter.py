# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest, os
import wc
from wc.proxy.Headers import WcMessage
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.filter import FilterProxyError, VirusFilter
from wc.log import initlog
from cStringIO import StringIO


class TestVirusFilter (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.config = wc.Configuration()
        wc.config['filters'] = ['VirusFilter']
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))
        VirusFilter.init_clamav_conf()


    def getAttrs (self):
        headers = WcMessage()
        headers['Content-Type'] = "text/html"
        return get_filterattrs("", [FILTER_RESPONSE_MODIFY], headers=headers)


    def filt (self, data, result):
        attrs = self.getAttrs()
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)


    def filtSize (self, size):
        attrs = self.getAttrs()
        i = 0L
        inc = 10000
        data = 'a'*inc
        while i <= size:
            applyfilter(FILTER_RESPONSE_MODIFY, data, 'filter', attrs)
            i += inc
        applyfilter(FILTER_RESPONSE_MODIFY, data, "finish", attrs)


    def testBasic (self):
        self.filt("""Test""", """Test""")


    def testTestSignature (self):
        self.filt("""$CEliacmaTrESTuScikgsn$FREE-TEST-SIGNATURE$EEEEE$""",
                  "")


    def testSizeLimit (self):
        size = VirusFilter.VirusFilter.MAX_FILE_BYTES+1
        self.assertRaises(FilterProxyError, self.filtSize, size)


suite = unittest.makeSuite(TestVirusFilter,'test')

if __name__ == '__main__':
    unittest.main()
