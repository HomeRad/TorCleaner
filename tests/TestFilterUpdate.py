# -*- coding: iso-8859-1 -*-
import unittest
import wc
from wc.log import *
from wc.update import update

class TestFilterUpdate (unittest.TestCase):
    def testUpdate (self):
        initlog("test/logging.conf")
        update(wc.Configuration(), dryrun=True)

if __name__ == '__main__':
    unittest.main()
