# -*- coding: iso-8859-1 -*-
"""test script to test javascript filtering"""

def filterfile (fname):
    print "filter", fname
    f = file(fname)
    attrs = get_filterattrs(fname, [FILTER_RESPONSE_MODIFY])
    s = ""
    data = f.read(4096)
    while data:
        try:
            s += applyfilter(FILTER_RESPONSE_MODIFY, data, 'filter', attrs)
        except FilterException, msg:
            pass
        data = f.read(4096)
    i = 1
    while 1:
        try:
            s += applyfilter(FILTER_RESPONSE_MODIFY, "", 'finish', attrs)
            break
        except FilterException, msg:
            proxy_poll(timeout=max(0, run_timers()))
        i+=1
        if i==100:
            # background downloading of javascript is too slow
            print "Test: oooooops"
            break
    print s

from test import disable_rating_rules
import wc
wc.config = wc.Configuration()
disable_rating_rules(wc.config)
wc.config['filters'] = ['Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
from wc.proxy import proxy_poll, run_timers
from wc.filter import FilterException
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
for i in range(14):
    fname = "test/html/script%d.html"%i
    filterfile(fname)
