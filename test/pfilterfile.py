#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""USAGE: test/run.sh test/pfilterfile.py <.html file>"""

import sys
if len(sys.argv)!=2:
    print __doc__
    sys.exit(1)
f = sys.argv[1]
data = file(f).read()
from test import initlog
initlog("test/logging.conf")
import wc
import wc.filter
wc.config = wc.Configuration()
wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
wc.config.init_filter_modules()
attrs = wc.filter.get_filterattrs(f, [wc.filter.FILTER_RESPONSE_MODIFY])
import hotshot
profile = hotshot.Profile("filter.prof")
profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, "+
            "data, 'finish', attrs)")
profile.close()

