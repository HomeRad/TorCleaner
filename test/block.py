#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main ():
    """USAGE: test/run.sh test/block.py <url>"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    url = sys.argv[1]
    data = "GET %s HTTP/1.0" % url
    from test import initlog
    initlog("test/logging.conf")
    import wc
    wc.config = wc.Configuration()
    wc.config['filters'] = ['Blocker',]
    wc.config.init_filter_modules()
    from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST
    attrs = get_filterattrs(url, [FILTER_REQUEST])
    print applyfilter(FILTER_REQUEST, data, 'finish', attrs)


if __name__=='__main__':
    _main()
