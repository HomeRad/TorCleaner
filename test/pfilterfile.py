#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""USAGE: test/run.sh test/pfilterfile.py <.html file>"""

import sys
import wc
import wc.filter

if len(sys.argv)!=2:
    print __doc__
    sys.exit(1)
f = sys.argv[1]
data = file(f).read()
from test import initlog
initlog("test/logging.conf")
wc.configuration.config = wc.configuration.Configuration()
wc.configuration.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
wc.configuration.config.init_filter_modules()
attrs = wc.filter.get_filterattrs(f, [wc.filter.FILTER_RESPONSE_MODIFY])

def _main ():
    import hotshot
    profile = hotshot.Profile("filter.prof")
    profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, "+
                "data, 'finish', attrs)")
    profile.close()

if __name__=='__main__':
    _main()
