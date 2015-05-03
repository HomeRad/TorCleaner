# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2010 Bastian Kleineidam
"""
Test virus filter.
"""
import unittest
import wc.filter.VirusFilter
from tests import has_clamav
from nose import SkipTest


class TestVirusFilter(unittest.TestCase):

    def testClean(self):
        if not has_clamav():
            raise SkipTest()
        data = ""
        infected, errors = self._scan(data)
        self.assertFalse(infected)
        self.assertFalse(errors)

    def testInfected(self):
        if not has_clamav():
            raise SkipTest()
        data = '<object data="&#109;s-its:mhtml:file://'+ \
               'C:\\foo.mht!${PATH}/' + \
               'EXPLOIT.CHM::' + \
               '/exploit.htm">'
        msg = 'stream: Exploit.HTML.MHTRedir.2n FOUND\n'
        infected, errors = self._scan(data)
        self.assertTrue(msg in infected)
        self.assertFalse(errors)

    def _scan(self, data):
        conf = wc.filter.VirusFilter.canonical_clamav_conf()
        clamconf = wc.filter.VirusFilter.ClamavConfig(conf)
        scanner = wc.filter.VirusFilter.ClamdScanner(clamconf)
        scanner.scan(data)
        scanner.close()
        return scanner.infected, scanner.errors
