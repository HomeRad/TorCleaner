#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest, os
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST
from wc.log import initlog
from tests import StandardTest

class TestBlocker (StandardTest):

    def init (self):
        self.url = "http://ads.realmedia.com/"
        wc.config = wc.Configuration()
        wc.config['filters'] = ['Blocker',]
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))

    def testBlocker (self):
        data = "GET %s HTTP/1.0" % self.url
        attrs = get_filterattrs(self.url, [FILTER_REQUEST])
        filtered = applyfilter(FILTER_REQUEST, data, 'finish', attrs)
        self.assert_(filtered.find("blocked.html")!=-1)


if __name__ == '__main__':
    unittest.main(defaultTest='TestBlocker')
else:
    suite = unittest.makeSuite(TestBlocker, 'test')
