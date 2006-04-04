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

import unittest
import tests
import wc.http.header


class TestHeader (tests.StandardTest):

    def test_add (self):
        d = wc.http.header.WcMessage()
	d['Via'] = 'foo\r'
	self.assert_('via' in d)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    return unittest.makeSuite(TestHeader)


if __name__ == '__main__':
    unittest.main()