# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

import wc, time
from test_support import TestFailed
reload(wc)
url = "http://ads.realmedia.com/"       
htmldata = "GET %s HTTP/1.0"%url
wc.config = wc.Configuration()
wc.config.init_filter_modules()
start = time.clock()
attrs = wc.filter.initStateObjects(url=url)
filtered = wc.filter.applyfilter(wc.filter.FILTER_REQUEST, htmldata,
           'finish', attrs)
stop = time.clock()
if filtered.find("blocked.html")==-1:
    raise TestFailed, "unblocked query %s"%htmldata
#print "time: %.3f seconds" % (stop-start)
