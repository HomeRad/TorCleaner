# -*- coding: iso-8859-1 -*-
"""test script to test filtering"""

import unittest
import wc
import wc.proxy.Headers
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY


class TestBinaryCharFilter (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.config = wc.Configuration()
        wc.config['filters'] = ['BinaryCharFilter']
        wc.config.init_filter_modules()

    def filt (self, data, result):
        headers = wc.proxy.Headers.WcMessage()
        headers['Content-Type'] = "text/html"
        attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY],
                                serverheaders=headers, headers=headers)
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)

    def test_quotes (self):
        self.filt("""These \x84Microsoft\x93 \x94chars\x94 are history.""",
                  """These "Microsoft" "chars" are history.""")
        self.filt("""\x91Retter\x92 Majak trifft in der Schlussminute.""",
                  """`Retter' Majak trifft in der Schlussminute.""")

    def test_null (self):
        self.filt("\x00", " ")


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBinaryCharFilter))
    return suite

if __name__ == '__main__':
    unittest.main()

