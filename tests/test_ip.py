# -*- coding: iso-8859-1 -*-

import unittest
from wc.network import iputil


class TestIp(unittest.TestCase):

    def testNames(self):
        hosts, nets = iputil.hosts2map(["www.kampfesser.net",
                                    "q2345qwer9 u2 42ß3 i34 uq3tu ",
                                    "2.3.4", ".3.4", "3.4", ".4", "4", ""])
        for host in iputil.resolve_host("www.kampfesser.net"):
            self.assertTrue(iputil.host_in_set(host, hosts, nets))
        self.assertTrue(not iputil.host_in_set("q2345qwer9 u2 42ß3 i34 uq3tu ", hosts, nets))
        self.assertTrue(not iputil.host_in_set("q2345qwer9", hosts, nets))
        self.assertTrue(not iputil.host_in_set("2.3.4", hosts, nets))
        self.assertTrue(not iputil.host_in_set(".3.4", hosts, nets))
        self.assertTrue(not iputil.host_in_set("3.4", hosts, nets))
        self.assertTrue(not iputil.host_in_set(".4", hosts, nets))
        self.assertTrue(not iputil.host_in_set("4", hosts, nets))
        self.assertTrue(not iputil.host_in_set("", hosts, nets))

    def testIPv4_1(self):
        hosts, nets = iputil.hosts2map(["1.2.3.4"])
        self.assertTrue(iputil.host_in_set("1.2.3.4", hosts, nets))

    def testBitmask0(self):
        """test the catch-all ip bitmask"""
        hosts, nets = iputil.hosts2map(["192.168.1.1/0"])
        self.assertTrue(iputil.host_in_set("1.1.1.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("0.0.0.0", hosts, nets))
        self.assertTrue(iputil.host_in_set("77.88.33.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("255.255.255.255", hosts, nets))

    def testBitmask8(self):
        hosts, nets = iputil.hosts2map(["192.168.1.1/8"])
        for i in xrange(255):
            self.assertTrue(iputil.host_in_set("192.168.1.%d"%i, hosts, nets))

    def testBitmask16(self):
        hosts, nets = iputil.hosts2map(["192.168.1.1/16"])
        for i in xrange(255):
            for j in xrange(255):
                self.assertTrue(iputil.host_in_set("192.168.%d.%d"%(i,j), hosts, nets))

    def testBitmask32(self):
        hosts, nets = iputil.hosts2map(["192.168.1.1/32"])
        self.assertTrue(not iputil.host_in_set("1.1.1.1", hosts, nets))
        self.assertTrue(not iputil.host_in_set("0.0.0.0", hosts, nets))
        self.assertTrue(not iputil.host_in_set("77.88.33.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("255.255.255.255", hosts, nets))

    def testNetmask1(self):
        hosts, nets = iputil.hosts2map(["192.168.1.1/255.255.255.0"])
        for i in xrange(255):
            self.assertTrue(iputil.host_in_set("192.168.1.%d"%i, hosts, nets))

    def testNetmask2(self):
        hosts, nets = iputil.hosts2map(["192.168.1.1/255.255.0.0"])
        for i in xrange(255):
            for j in xrange(255):
                self.assertTrue(iputil.host_in_set("192.168.%d.%d"%(i,j), hosts, nets))

    def testNetmask4(self):
        """test the catch-all netmask"""
        hosts, nets = iputil.hosts2map(["192.168.1.1/0.0.0.0"])
        self.assertTrue(iputil.host_in_set("1.1.1.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("0.0.0.0", hosts, nets))
        self.assertTrue(iputil.host_in_set("77.88.33.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("255.255.255.255", hosts, nets))
        hosts, nets = iputil.hosts2map(["1.1.1.1/0.0.0.0"])
        self.assertTrue(iputil.host_in_set("1.1.1.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("0.0.0.0", hosts, nets))
        self.assertTrue(iputil.host_in_set("77.88.33.1", hosts, nets))
        self.assertTrue(iputil.host_in_set("255.255.255.255", hosts, nets))

    def testIPv6_1(self):
        hosts, nets = iputil.hosts2map(["::0"])
        # XXX

    def testIPv6_2(self):
        hosts, nets = iputil.hosts2map(["1::"])
        # XXX

    def testIPv6_3(self):
        hosts, nets = iputil.hosts2map(["1::1"])
        # XXX

    def testIPv6_4(self):
        hosts, nets = iputil.hosts2map(["fe00::0"])
        # XXX

    def testNetmask(self):
        for i in xrange(32):
            hosts, nets = iputil.hosts2map(["144.145.146.1/%d"%i])
