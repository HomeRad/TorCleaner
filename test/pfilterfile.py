#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())
import profile, wc

f = sys.argv[1]
data = file(f).read()
import wc, time
wc.DebugLevel = 3
wc.config = wc.Configuration()
wc.config['filters'] = ['Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
attrs = wc.filter.initStateObjects(url=f)
name = "filter.prof"
profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'finish', attrs)", name)
