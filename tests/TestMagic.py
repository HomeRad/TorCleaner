# -*- coding: iso-8859-1 -*-
"""magic(5) tester"""

import unittest, os
from wc import magic
from test import initlog

class TestMagic (unittest.TestCase):

    def setUp (self):
        initlog("test/logging.conf")
        self.basedir = os.path.join(os.getcwd(), "tests", "magic")


    def testHtml (self):
        self.doMagic("test.html", "text/html")


    def doMagic (self, filename, expected):
        fp = file(os.path.join(self.basedir, filename), 'rb')
        classify = magic.classify(fp)
        self.assertEqual(classify, expected)


if __name__ == '__main__':
    unittest.main()
