#!/usr/bin/python2.3
import sys, os, profile
try:
    import wc
    raise SystemExit("Global WebCleaner installation found")
except ImportError:
    sys.path.insert(0, os.getcwd())
    import wc

f = sys.argv[1]
data = file(f).read()
wc.DebugLevel = 3
wc.config = wc.Configuration()
wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
attrs = wc.filter.initStateObjects(url=f)
name = "filter.prof"
profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'finish', attrs)", name)
