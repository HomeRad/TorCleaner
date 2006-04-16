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
import tests
import wc
import wc.configuration
import wc.update


class NoLog (object):
    def write (self, s):
        pass


class TestUpdate (unittest.TestCase):

    def setUp (self):
        self.nolog = NoLog()
        self.config = wc.configuration.init()

    def testUpdateFilter (self):
        wc.update.update_filter(self.config, dryrun=True, log=self.nolog)

    def testUpdateRatings (self):
        wc.update.update_ratings(self.config, dryrun=True, log=self.nolog)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUpdate))
    return suite


if __name__ == '__main__':
    unittest.main()
