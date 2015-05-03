# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Test script to test filtering.
"""
import unittest
import random
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY


class TestReplacer(unittest.TestCase):

    def init(self):
        super(TestReplacer, self).init()
        wc.configuration.init()
        wc.configuration.config['filters'] = ['Replacer']
        wc.configuration.config.init_filter_modules()

    def testReplaceRandom(self):
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY])
        # filter random data, should not raise any exception
        data = []
        for dummy in xrange(1024):
            data.append(chr(random.randint(0, 255)))
        data = "".join(data)
        applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)

    def testReplaceNonAscii(self):
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY])
        data = "äöü asdfö"
        applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)
