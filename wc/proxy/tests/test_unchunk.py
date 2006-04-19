# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
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
import unittest
import wc.proxy.decoder.UnchunkStream
import wc.dummy


class TestUnchunk (unittest.TestCase):

    def testUnchunk (self):
        dummy = wc.dummy.Dummy()
        unchunker = wc.proxy.decoder.UnchunkStream.UnchunkStream(dummy)
        data = "a"*0x30
        s = "000000000030\r\n%s\r\n0\r\n\r\n" % data
        self.assertEqual(data, unchunker.process(s))


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUnchunk))
    return suite


if __name__ == '__main__':
    unittest.main()
