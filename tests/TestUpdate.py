# -*- coding: iso-8859-1 -*-
import unittest
import wc
from wc.log import *
import wc.update
import StandardTest


class NoLog (object):
    def write (self, s):
        pass


class TestUpdate (StandardTest.StandardTest):

    def init (self):
        super(TestUpdate, self).init()
        self.nolog = NoLog()
        self.config = wc.Configuration()

    def testUpdateFilter (self):
        wc.update.update_filter(self.config, dryrun=True, log=self.nolog)

    def testUpdateRatings (self):
        wc.update.update_ratings(self.config, dryrun=True, log=self.nolog)


if __name__ == '__main__':
    unittest.main(defaultTest='TestUpdate')
else:
    suite = unittest.makeSuite(TestUpdate, 'test')
