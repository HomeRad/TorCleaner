# -*- coding: iso-8859-1 -*-
import unittest
import wc
from wc.log import *
from wc.update import update_filter, update_ratings

class TestUpdate (unittest.TestCase):
    def setUp (self):
        initlog("test/logging.conf")
        self.config = wc.Configuration()


    def testUpdateFilter (self):
        update_filter(self.config, dryrun=True)


    def testUpdateRatings (self):
        update_ratings(self.config, dryrun=True)


if __name__ == '__main__':
    unittest.main()
