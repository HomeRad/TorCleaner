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
    from wc.proxy.Headers import WcMessage
    wc.config = wc.init()
    wc.config['filters'] = ['Blocker',]
    wc.config.init_filter_modules()
    from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST
    headers = WcMessage()
    headers['Content-Type'] = "text/html"
    attrs = get_filterattrs(url, [FILTER_REQUEST], headers=headers)
    print applyfilter(FILTER_REQUEST, data, 'finish', attrs)


if __name__=='__main__':
    _main()
