#!/usr/bin/env python2
""" test script to test filtering"""

htmldata = """GET http://ads.realmedia.com/ HTTP/1.0"""

import wc,time
wc.config.init_filter_modules()
wc.DebugLevel = 0
start = time.clock()
attrs = wc.filter.initStateObjects()
filtered = wc.filter.applyfilter(wc.filter.FILTER_REQUEST, htmldata,
           'finish', attrs)
stop = time.clock()
if filtered.find("blocked.html")==-1:
    raise TestFailed, "unblocked query %s"%htmldata
#print "time: %.3f seconds" % (stop-start)
