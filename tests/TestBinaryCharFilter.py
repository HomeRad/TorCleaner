# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest, os
import wc
from wc.proxy.Headers import WcMessage
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.log import initlog


class TestBinaryCharFilter (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.set_config(wc.Configuration())
        wc.config['filters'] = ['BinaryCharFilter']
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))


    def filt (self, data, result):
        headers = WcMessage()
        headers['Content-Type'] = "text/html"
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY], headers=headers)
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)


    def _estQuotes (self):
        self.filt("""These \x84Microsoft\x93 \x94chars\x94 are history.""",
                  """These "Microsoft" "chars" are history.""")
        self.filt("""\x91Retter\x92 Majak trifft in der Schlussminute.""",
                  """`Retter' Majak trifft in der Schlussminute.""")


    def testNull (self):
        self.filt("\x00", " ")


suite = unittest.makeSuite(TestBinaryCharFilter,'test')

if __name__ == '__main__':
    unittest.main()
