# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Test virus filter.
"""
import unittest
import tests
import wc.filter.VirusFilter


class TestVirusFilter (tests.StandardTest):

    needed_resources = ['clamav']

    def testClean (self):
        data = ""
        infected, errors = self._scan(data)
        self.assertFalse(infected)
        self.assertFalse(errors)

    def testInfected (self):
        data = '<object data="&#109;s-its:mhtml:file://'+ \
               'C:\\foo.mht!${PATH}/' + \
               'EXPLOIT.CHM::' + \
               '/exploit.htm">'
        msg = 'stream: Exploit.HTML.MHT-7 FOUND\n'
        infected, errors = self._scan(data)
        self.assert_(msg in infected)
        self.assertFalse(errors)

    def _scan (self, data):
        conf = wc.filter.VirusFilter.canonical_clamav_conf()
        clamconf = wc.filter.VirusFilter.ClamavConfig(conf)
        scanner = wc.filter.VirusFilter.ClamdScanner(clamconf)
        scanner.scan(data)
        scanner.close()
        return scanner.infected, scanner.errors


def test_suite ():
    return unittest.makeSuite(TestVirusFilter)


if __name__ == '__main__':
    unittest.main()