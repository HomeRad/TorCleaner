# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

from test_support import TestFailed
url = "http://ads.realmedia.com/"
data = "GET %s HTTP/1.0" % url
from test import initlog
initlog("test/logging.conf")
import wc
wc.config = wc.Configuration()
wc.config.init_filter_modules()
from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST
attrs = get_filterattrs(url, [FILTER_REQUEST])
filtered = applyfilter(FILTER_REQUEST, data, 'finish', attrs)
if filtered.find("blocked.html")==-1:
    raise TestFailed, "unblocked query %s"%data
