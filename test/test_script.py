# -*- coding: iso-8859-1 -*-
"""test script to test javascript filtering"""

def filterfile (fname):
    print "filter", fname
    f = file(fname)
    attrs = wc.filter.initStateObjects(url=fname)
    filtered = ""
    data = f.read(4096)
    while data:
        try:
            filtered += wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                                              data, 'filter', attrs)
        except FilterException, msg:
            pass
        data = f.read(4096)
    i = 1
    while 1:
        try:
            filtered += wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                                             "", 'finish', attrs)
            break
        except FilterException, msg:
            proxy_poll(timeout=max(0, run_timers()))
        i+=1
        if i==100:
            # background downloading of javascript is too slow
            print "Test: oooooops"
            break
    print filtered

from test import initlog, disable_pics_rules
initlog("test/logging.conf")
import wc
wc.config = wc.Configuration()
disable_pics_rules(wc.config)
wc.config['filters'] = ['Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
from wc.proxy import proxy_poll, run_timers
from wc.filter import FilterException
for i in range(11):
    fname = "test/html/script%d.html"%i
    filterfile(fname)

