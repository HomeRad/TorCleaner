# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
import unittest
import wc.configuration
import wc.update


class NoLog(object):
    def write(self, s):
        pass


class TestUpdate(unittest.TestCase):

    def setUp(self):
        self.nolog = NoLog()
        self.config = wc.configuration.init()

    def testUpdateFilter(self):
        wc.update.update_filter(self.config, dryrun=True, log=self.nolog)

    def testUpdateRatings(self):
        wc.update.update_ratings(self.config, dryrun=True, log=self.nolog)
