# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY


class TestBinaryCharFilter (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.config = wc.Configuration()
        wc.config['filters'] = ['BinaryCharFilter']
        wc.config.init_filter_modules()


    def filt (self, data, result):
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)


    def testQuotes (self):
        self.filt("""These \x84Microsoft\x93 \x94chars\x94 are history.""",
                  """These "Microsoft" "chars" are history.""")
        self.filt("""\x91Retter\x92 Majak trifft in der Schlussminute.""",
                  """`Retter' Majak trifft in der Schlussminute.""")


    def testNull (self):
        self.filt("\x00", " ")


if __name__ == '__main__':
    unittest.main()
