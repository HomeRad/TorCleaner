# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
Test dummy object.
"""

import unittest

import wc.strformat
import wc.dummy
from wc.tests import MsgTestCase


class TestDummy (MsgTestCase):
    """
    Test dummy object.
    """

    def test_creation (self):
        dummy = wc.dummy.Dummy()
        dummy = wc.dummy.Dummy("1")
        dummy = wc.dummy.Dummy("1", "2")
        dummy = wc.dummy.Dummy(a=1, b=2)
        dummy = wc.dummy.Dummy("1", a=None, b=2)

    def test_attributes (self):
        dummy = wc.dummy.Dummy()
        dummy.hulla
        dummy.hulla.bulla
        dummy.hulla = 1
        del dummy.wulla
        del dummy.wulla.mulla

    def test_methods (self):
        dummy = wc.dummy.Dummy()
        dummy.hulla()
        dummy.hulla().bulla()

    def test_indexes (self):
        dummy = wc.dummy.Dummy()
        dummy[1] = dummy[2]
        dummy[1][-1]
        dummy[1:3] = None


def test_suite ():
    """
    Build and return a TestSuite.
    """
    return unittest.makeSuite(TestDummy)


if __name__ == '__main__':
    unittest.main()
