# -*- coding: iso-8859-1 -*-
"""test script to test clamav virus scanning"""

import unittest, os
import wc
from wc.filter.VirusFilter import ClamavConfig
from wc.log import initlog


class TestClamdScanner (unittest.TestCase):
    """Test the clamav daemon stream scanner"""

    def setUp (self):
        wc.config = wc.Configuration()
        self.clamav_conf = ClamavConfig(wc.config['clamavconf'])
        initlog(os.path.join("test", "logging.conf"))


    def test1 (self):
        data = file(os.path.join("tests", "virus", "test1")).read()
        self.scan(data)


    def scan (self, data):
        sock, host = self.clamav_conf.new_connection()
        wsock = self.clamav_conf.new_scansock(sock, host)
        wsock.sendall(data)
        wsock.close()
        infected = []
        errors = []
        data = sock.recv(4096)
        while data:
            if "FOUND\n" in data:
                infected.append(data)
            if "ERROR\n" in data:
                errors.append(data)
            data = sock.recv(4096)
        self.assert_(infected)
        self.assert_("ClamAV-Test-Signature FOUND" in infected[0])
        self.assert_(not errors)


if __name__ == '__main__':
    unittest.main()
