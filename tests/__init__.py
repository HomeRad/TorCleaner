# -*- coding: iso-8859-1 -*-
"""WebCleaner unittests are defined here"""

import unittest

class StandardTest (unittest.TestCase, object):
    """A class augmenting the default unittest TestCase by init() and
       shutdown() methods, each called only once before and after
       execution of all test methods.
    """
    def __call__(self, result=None):
        self.init()
        super(StandardTest, self).__call__(result=result)
        self.shutdown()

    def init (self):
        pass

    def shutdown (self):
        pass
