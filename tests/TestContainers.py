# -*- coding: iso-8859-1 -*-
"""test sorted dictionary routines"""

import unittest
import random
import wc.containers
import StandardTest


class TestContainers (StandardTest.StandardTest):

    def testListDictInsert (self):
        d = wc.containers.ListDict()
        d[2] = 1
        d[1] = 2
        self.assert_(2 in d)
        self.assert_(1 in d)

    def testListDictDelete (self):
        d = wc.containers.ListDict()
        d[2] = 1
        d[1] = 2
        del d[1]
        self.assert_(2 in d)
        self.assert_(1 not in d)

    def testListDictUpdate (self):
        d = wc.containers.ListDict()
        d[2] = 1
        d[1] = 2
        d[1] = 1
        self.assertEqual(d[1], 1)

    def testListDictSorting (self):
        d = wc.containers.ListDict()
        toinsert = random.sample(xrange(10000000), 60)
        for x in toinsert:
            d[x] = x
        for i, k in enumerate(d.keys()):
            self.assertEqual(d[k], toinsert[i])

    def testSetListAppend (self):
        l = wc.containers.SetList()
        l.append(1)
        l.append(1)
        self.assertEqual(len(l), 1)
        l = wc.containers.SetList()
        l.append(1)
        l.append(2)
        l.append(1)
        self.assertEqual(len(l), 2)

    def testSetListExtend (self):
        l = wc.containers.SetList()
        l.extend([1, 2, 1])
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0], 1)
        self.assertEqual(l[1], 2)

    def testSetListSetItem (self):
        l = wc.containers.SetList()
        l.extend([1,2,3])
        l[1] = 3
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0], 1)
        self.assertEqual(l[1], 3)

if __name__ == '__main__':
    unittest.main(defaultTest='TestContainers')
else:
    suite = unittest.makeSuite(TestContainers, 'test')
