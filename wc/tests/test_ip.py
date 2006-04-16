# -*- coding: iso-8859-1 -*-

import unittest
import tests
import wc.ip


class TestIp (unittest.TestCase):

    def testNames (self):
        hosts, nets = wc.ip.hosts2map(["www.kampfesser.net",
                                    "q2345qwer9 u2 42�3 i34 uq3tu ",
                                    "2.3.4", ".3.4", "3.4", ".4", "4", ""])
        for host in wc.ip.resolve_host("www.kampfesser.net"):
            self.assert_(wc.ip.host_in_set(host, hosts, nets))
        self.assert_(not wc.ip.host_in_set("q2345qwer9 u2 42�3 i34 uq3tu ", hosts, nets))
        self.assert_(not wc.ip.host_in_set("q2345qwer9", hosts, nets))
        self.assert_(not wc.ip.host_in_set("2.3.4", hosts, nets))
        self.assert_(not wc.ip.host_in_set(".3.4", hosts, nets))
        self.assert_(not wc.ip.host_in_set("3.4", hosts, nets))
        self.assert_(not wc.ip.host_in_set(".4", hosts, nets))
        self.assert_(not wc.ip.host_in_set("4", hosts, nets))
        self.assert_(not wc.ip.host_in_set("", hosts, nets))

    def testIPv4_1 (self):
        hosts, nets = wc.ip.hosts2map(["1.2.3.4"])
        self.assert_(wc.ip.host_in_set("1.2.3.4", hosts, nets))

    def testBitmask0 (self):
        """test the catch-all ip bitmask"""
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/0"])
        self.assert_(wc.ip.host_in_set("1.1.1.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("0.0.0.0", hosts, nets))
        self.assert_(wc.ip.host_in_set("77.88.33.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("255.255.255.255", hosts, nets))

    def testBitmask8 (self):
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/8"])
        for i in range(255):
            self.assert_(wc.ip.host_in_set("192.168.1.%d"%i, hosts, nets))

    def testBitmask16 (self):
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/16"])
        for i in range(255):
            for j in range(255):
                self.assert_(wc.ip.host_in_set("192.168.%d.%d"%(i,j), hosts, nets))

    def testBitmask32 (self):
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/32"])
        self.assert_(not wc.ip.host_in_set("1.1.1.1", hosts, nets))
        self.assert_(not wc.ip.host_in_set("0.0.0.0", hosts, nets))
        self.assert_(not wc.ip.host_in_set("77.88.33.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("255.255.255.255", hosts, nets))

    def testNetmask1 (self):
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/255.255.255.0"])
        for i in range(255):
            self.assert_(wc.ip.host_in_set("192.168.1.%d"%i, hosts, nets))

    def testNetmask2 (self):
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/255.255.0.0"])
        for i in range(255):
            for j in range(255):
                self.assert_(wc.ip.host_in_set("192.168.%d.%d"%(i,j), hosts, nets))

    def testNetmask4 (self):
        """test the catch-all netmask"""
        hosts, nets = wc.ip.hosts2map(["192.168.1.1/0.0.0.0"])
        self.assert_(wc.ip.host_in_set("1.1.1.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("0.0.0.0", hosts, nets))
        self.assert_(wc.ip.host_in_set("77.88.33.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("255.255.255.255", hosts, nets))
        hosts, nets = wc.ip.hosts2map(["1.1.1.1/0.0.0.0"])
        self.assert_(wc.ip.host_in_set("1.1.1.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("0.0.0.0", hosts, nets))
        self.assert_(wc.ip.host_in_set("77.88.33.1", hosts, nets))
        self.assert_(wc.ip.host_in_set("255.255.255.255", hosts, nets))

    def testIPv6_1 (self):
        hosts, nets = wc.ip.hosts2map(["::0"])
        # XXX

    def testIPv6_2 (self):
        hosts, nets = wc.ip.hosts2map(["1::"])
        # XXX

    def testIPv6_3 (self):
        hosts, nets = wc.ip.hosts2map(["1::1"])
        # XXX

    def testIPv6_4 (self):
        hosts, nets = wc.ip.hosts2map(["fe00::0"])
        # XXX

    def testNetmask (self):
        for i in range(32):
            hosts, nets = wc.ip.hosts2map(["144.145.146.1/%d"%i])


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIp))
    return suite

if __name__ == '__main__':
    unittest.main()
