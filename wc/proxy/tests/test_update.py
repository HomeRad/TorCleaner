# -*- coding: iso-8859-1 -*-
import unittest
import wc
import wc.update


class NoLog (object):
    def write (self, s):
        pass


class TestUpdate (unittest.TestCase):

    def setUp (self):
        self.nolog = NoLog()
        self.config = wc.Configuration()

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

