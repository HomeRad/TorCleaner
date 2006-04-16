# -*- coding: iso-8859-1 -*-
"""
A magic(5) tester.
"""

import unittest
import os
import tests
from wc.magic import convert, classify

class TestMagic (unittest.TestCase):

    def setUp (self):
        self.basedir = os.path.join(os.getcwd(), "wc", "magic", "tests")

    def doMagic (self, filename, expected):
        fp = file(os.path.join(self.basedir, filename), 'rb')
        self.assertEqual(classify(fp), expected)

    def test_html (self):
        self.doMagic("test.html", "text/html")

    def test_convert (self):
        self.assertEqual(255, convert.convert(r"0xFF"))
        self.assertEqual(255, convert.convert(r"\xFF"))
        self.assertEqual(63, convert.convert(r"077"))
        self.assertEqual(63, convert.convert(r"\77"))
        # the E is not used
        self.assertEqual(127, convert.convert(r"\177E"))
        self.assertEqual(2, convert.convert(r"02f7"))

    def test_size_number (self):
        self.assertEqual(3, convert.size_number(r"100qwerty"))
        self.assertEqual(3, convert.size_number(r"100FFF"))
        self.assertEqual(2, convert.size_number(r"\77FF"))
        self.assertEqual(2, convert.size_number(r"\XFFG"))
        self.assertEqual(1, convert.size_number(r"02f7"))

    def test_index_number (self):
        self.assertEqual(0, convert.index_number(r"0XF"))
        self.assertEqual(0, convert.index_number(r"\XF"))
        self.assertEqual(-1, convert.index_number(r"FF\FFGG"))
        self.assertEqual(2, convert.index_number(r"FF\7"))
        self.assertEqual(3, convert.index_number(r"FFF\XFFGG"))
        self.assertEqual(2, convert.index_number(r"FF\XFFGG"))

    def test_convert_endian (self):
        # 0000 0001 -->     1
        # 0001 0000 -->    16
        # 0001 1000 -->    24
        # 1000 0001 -->   129
        # 0000 0001 1000 0000 -->   384
        # 1000 0000 0000 0001 --> 32769
        # 0000 0000 0000 0001 1000 0000 0000 0000 --> 98304
        # 0000 0000 1000 0000 0000 0001 0000 0000 --> 8388864
        # 1000 0000 0000 0000 0000 0000 0000 0001 --> 2147483649
        self.assertEqual(1, convert.little2(chr(1)+chr(0)))
        self.assertEqual(16, convert.little2(chr(16)+chr(0)))
        self.assertEqual(1, convert.big2(chr(0)+chr(1)))
        self.assertEqual(16, convert.big2(chr(0)+chr(16)))
        self.assertEqual(2147483649, convert.little4(chr(1)+chr(0)+chr(0)+chr(128)))
        self.assertEqual(2147483649, convert.big4(chr(128)+chr(0)+chr(0)+chr(1)))


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMagic))
    return suite


if __name__ == '__main__':
    unittest.main()
