# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

import wc, time
from test_support import TestFailed
url = "http://ads.realmedia.com/"
data = "GET %s HTTP/1.0" % url
from wc.log import initlog
initlog("test/logging.conf")
wc.config = wc.Configuration()
wc.config.init_filter_modules()
attrs = wc.filter.initStateObjects(url=url)
filtered = \
      wc.filter.applyfilter(wc.filter.FILTER_REQUEST, data, 'finish', attrs)
if filtered.find("blocked.html")==-1:
    raise TestFailed, "unblocked query %s"%data
