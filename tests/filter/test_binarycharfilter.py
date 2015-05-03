# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Test script to test filtering.
"""

import unittest
import wc.configuration
import wc.proxy.Headers
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY


class TestBinaryCharFilter(unittest.TestCase):
    """
    All these tests work with a _default_ filter configuration.
    If you change any of the *.zap filter configs, tests can fail...
    """

    def setUp(self):
        wc.configuration.init()
        wc.configuration.config['filters'] = ['BinaryCharFilter']
        wc.configuration.config.init_filter_modules()

    def filt(self, data, result):
        headers = wc.http.header.WcMessage()
        headers['Content-Type'] = "text/html"
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY],
                                serverheaders=headers, headers=headers)
        filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)

    def test_quotes(self):
        self.filt("""These \x84Microsoft\x93 \x94chars\x94 are history.""",
                  """These "Microsoft" "chars" are history.""")
        self.filt("""\x91Retter\x92 Majak trifft in der Schlussminute.""",
                  """`Retter' Majak trifft in der Schlussminute.""")

    def test_null(self):
        self.filt("\x00", " ")
