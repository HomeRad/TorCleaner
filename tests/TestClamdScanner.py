# -*- coding: iso-8859-1 -*-
"""test script to test clamav virus scanning"""

import unittest, os
import wc
from wc.filter.VirusFilter import ClamavConfig, ClamdScanner
from wc.log import initlog


class TestClamdScanner (unittest.TestCase):
    """Test the clamav daemon stream scanner"""

    def setUp (self):
        wc.config = wc.Configuration()
        initlog(os.path.join("test", "logging.conf"))
        clamav_conf = ClamavConfig(wc.config['clamavconf'])
        self.scanner = ClamdScanner(clamav_conf)


    def test1 (self):
        data = file(os.path.join("tests", "virus", "test1")).read()
        self.scanner.scan(data)
        self.scanner.scan(data)
        self.scanner.scan(data)
        self.scanner.close()
        self.assert_(self.scanner.infected)
        self.assert_("ClamAV-Test-Signature FOUND" in self.scanner.infected[0])
        self.assert_(not self.scanner.errors)


if __name__ == '__main__':
    unittest.main()
