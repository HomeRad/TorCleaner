#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""configuration loading profiling"""
import sys, os, profile
try:
    import wc
except ImportError:
    print "using local development version"
    import os
    sys.path.insert(0, os.getcwd())
    import wc

from wc.log import initlog
initlog("test/logging.conf")
name = "filter.prof"
profile.run("config = wc.Configuration()", name)
#wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
#wc.config.init_filter_modules()
