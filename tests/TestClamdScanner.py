# -*- coding: iso-8859-1 -*-
"""test script to test clamav virus scanning"""

import unittest
import os
import wc
from wc.filter.VirusFilter import ClamavConfig, ClamdScanner
import StandardTest


class TestClamdScanner (StandardTest.StandardTest):
    """Test the clamav daemon stream scanner"""

    def init (self):
        super(TestClamdScanner, self).init()
        wc.config = wc.Configuration()
        self.clamav_conf = ClamavConfig(wc.config['clamavconf'])

    def testPlain (self):
        self.scan("test1")

    def testBz2 (self):
        self.scan("test1.bz2")

    def testBadext (self):
        self.scan("test2.badext")

    def testZip (self):
        self.scan("test2.zip")

    def _testRar (self):
        self.scan("test3.rar")

    def scan (self, filename):
        filename =  os.path.join("tests", "virus", filename)
        scanner = ClamdScanner(self.clamav_conf)
        scanner.scan(file(filename).read())
        scanner.close()
        for msg in scanner.errors:
            print "Scan error", msg,
        self.assert_(scanner.infected)
        self.assert_("ClamAV-Test-Signature FOUND" in scanner.infected[0])
        self.assert_(not scanner.errors)


if __name__ == '__main__':
    unittest.main(defaultTest='TestClamdScanner')
else:
    suite = unittest.makeSuite(TestClamdScanner, 'test')

