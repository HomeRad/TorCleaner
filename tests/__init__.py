# -*- coding: iso-8859-1 -*-
"""WebCleaner unittests are defined here"""

import unittest, os
from wc.log import initlog

class StandardTest (unittest.TestCase, object):
    """A class augmenting the default unittest TestCase by init() and
       shutdown() methods, each called only once before and after
       execution of all test methods.
    """
    def __call__(self, result=None):
        self.showAll = result.showAll
        self.init()
        try:
            return super(StandardTest, self).__call__(result=result)
        finally:
            self.shutdown()

    def init (self):
        """base initialization of the logging framework"""
        initlog(os.path.join("test", "logging.conf"))

    def shutdown (self):
        pass
