# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2010 Bastian Kleineidam
"""
Test script to test filtering.
"""

import unittest
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, STAGE_REQUEST


class TestBlocker(unittest.TestCase):

    def setUp(self):
        self.url = "http://ads.realmedia.com/"
        wc.configuration.init()
        wc.configuration.config['filters'] = ['Blocker',]
        wc.configuration.config.init_filter_modules()

    def test_block(self):
        data = "GET %s HTTP/1.0" % self.url
        attrs = get_filterattrs(self.url, "localhost", [STAGE_REQUEST])
        filtered = applyfilter(STAGE_REQUEST, data, 'finish', attrs)
        self.assertTrue(filtered.find("blocked.html")!=-1)
