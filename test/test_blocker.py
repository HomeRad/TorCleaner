""" test script to test filtering"""

import wc, time
from test_support import TestFailed
reload(wc)
htmldata = """GET http://ads.realmedia.com/ HTTP/1.0"""
wc.config = wc.Configuration()
wc.config.init_filter_modules()
wc.DebugLevel = 0
start = time.clock()
attrs = wc.filter.initStateObjects(url="http://ads.realmedia.com/")
filtered = wc.filter.applyfilter(wc.filter.FILTER_REQUEST, htmldata,
           'finish', attrs)
stop = time.clock()
if filtered.find("blocked.html")==-1:
    raise TestFailed, "unblocked query %s"%htmldata
#print "time: %.3f seconds" % (stop-start)
