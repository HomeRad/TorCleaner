# -*- coding: iso-8859-1 -*-
"""test sorted dictionary routines"""

import unittest, random
from wc.parser import SortedDict


class TestSortedDict (unittest.TestCase):
    def testInsert (self):
        d = SortedDict()
        d[2] = 1
        d[1] = 2
        self.assert_(2 in d)
        self.assert_(1 in d)


    def testDelete (self):
        d = SortedDict()
        d[2] = 1
        d[1] = 2
        del d[1]
        self.assert_(2 in d)
        self.assert_(1 not in d)


    def testUpdate (self):
        d = SortedDict()
        d[2] = 1
        d[1] = 2
        d[1] = 1
        self.assertEqual(d[1], 1)


    def testSorting (self):
        d = SortedDict()
        toinsert = random.sample(xrange(10000000), 60)
        for x in toinsert:
            d[x] = x
        for i, k in enumerate(d.keys()):
            self.assertEqual(d[k], toinsert[i])


if __name__ == '__main__':
    unittest.main()
else:
    suite = unittest.makeSuite(TestSortedDict, 'test')
