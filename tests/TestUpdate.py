# -*- coding: iso-8859-1 -*-
import unittest
import wc
from wc.log import *
from wc.update import update_filter, update_ratings

class NoLog (object):
    def write (self, s):
        pass


class TestUpdate (unittest.TestCase):
    def setUp (self):
        self.nolog = NoLog()
        initlog("test/logging.conf")
        self.config = wc.Configuration()


    def testUpdateFilter (self):
        update_filter(self.config, dryrun=True, log=self.nolog)


    def testUpdateRatings (self):
        update_ratings(self.config, dryrun=True, log=self.nolog)


suite = unittest.makeSuite(TestUpdate,'test')

if __name__ == '__main__':
    unittest.main()
