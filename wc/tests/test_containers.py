# -*- coding: iso-8859-1 -*-
"""test container routines"""
# Copyright (C) 2004  Bastian Kleineidam
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
import random
import wc.containers


class TestListDict (unittest.TestCase):
    """test list dictionary routines"""

    def setUp (self):
        """set up self.d as empty listdict"""
        self.d = wc.containers.ListDict()

    def test_insert (self):
        """test insertion order"""
        self.assert_(not self.d)
        self.d[2] = 1
        self.d[1] = 2
        self.assert_(2 in self.d)
        self.assert_(1 in self.d)

    def test_delete (self):
        """test deletion order"""
        self.assert_(not self.d)
        self.d[2] = 1
        self.d[1] = 2
        del self.d[1]
        self.assert_(2 in self.d)
        self.assert_(1 not in self.d)

    def test_update (self):
        """test update order"""
        self.assert_(not self.d)
        self.d[2] = 1
        self.d[1] = 2
        self.d[1] = 1
        self.assertEqual(self.d[1], 1)

    def test_sorting (self):
        """test sorting"""
        self.assert_(not self.d)
        toinsert = random.sample(xrange(10000000), 60)
        for x in toinsert:
            self.d[x] = x
        for i, k in enumerate(self.d.keys()):
            self.assertEqual(self.d[k], toinsert[i])


class TestSetList (unittest.TestCase):
    """test set list routines"""

    def setUp (self):
        """set up self.l as empty setlist"""
        self.l = wc.containers.SetList()

    def test_append (self):
        """test append and equal elements"""
        self.assert_(not self.l)
        self.l.append(1)
        self.l.append(1)
        self.assertEqual(len(self.l), 1)

    def test_append2 (self):
        """test append and equal elements 2"""
        self.assert_(not self.l)
        self.l.append(1)
        self.l.append(2)
        self.l.append(1)
        self.assertEqual(len(self.l), 2)

    def test_extend (self):
        """test extend and equal elements"""
        self.assert_(not self.l)
        self.l.extend([1, 2, 1])
        self.assertEqual(len(self.l), 2)
        self.assertEqual(self.l[0], 1)
        self.assertEqual(self.l[1], 2)

    def test_setitem (self):
        """test setting of equal elements"""
        self.assert_(not self.l)
        self.l.extend([1, 2, 3])
        self.l[1] = 3
        self.assertEqual(len(self.l), 2)
        self.assertEqual(self.l[0], 1)
        self.assertEqual(self.l[1], 3)


class TestLRU (unittest.TestCase):
    """test routines of LRU queue"""

    def setUp (self):
        """set up self.lru as empty LRU queue"""
        self.count = 4
        self.lru = wc.containers.LRU(self.count)

    def test_len (self):
        """test LRU length correctness"""
        self.assertEqual(len(self.lru), 0)
        for i in range(self.count):
            self.lru[str(i)] = str(i)
            self.assertEqual(len(self.lru), i+1)
        # overflow (inserting (self.count+1)th element
        self.lru[""] = ""
        self.assertEqual(len(self.lru), self.count)

    def test_overflow (self):
        """test LRU capacity overflow"""
        for i in range(self.count):
            self.lru[str(i)] = str(i)
        # overflow (inserting (self.count+1)th element
        self.lru[""] = ""
        # zero must have been deleted
        self.assert_(not self.lru.has_key('0'))


def test_suite ():
    """build and return a TestSuite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestListDict))
    suite.addTest(unittest.makeSuite(TestSetList))
    suite.addTest(unittest.makeSuite(TestLRU))
    return suite

if __name__ == '__main__':
    unittest.main()