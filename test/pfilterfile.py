#!/usr/bin/env python
import sys
sys.path.insert(0, ".")
import profile, wc

file = sys.argv[1]
data = open(file).read()
import wc, time
wc.DebugLevel = 3
wc.config = wc.Configuration()
wc.config['filters'] = ['Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
attrs = wc.filter.initStateObjects(url=file)
name = "filter.prof"
profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'finish', attrs)", name)
