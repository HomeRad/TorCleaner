#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main ():
    """USAGE: test/run.sh test/filterfile.py <.html file>"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    fname = sys.argv[1]
    if fname=="-":
        f = sys.stdin
    else:
        f = file(fname)
    from test import initlog, disable_rating_rules
    initlog("test/logging.conf")
    import wc
    wc.config = wc.Configuration()
    disable_rating_rules(wc.config)
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    from wc.proxy import proxy_poll, run_timers
    from wc.proxy.Headers import WcMessage
    from wc.filter import FilterException, applyfilter, get_filterattrs
    from wc.filter import FILTER_RESPONSE_MODIFY
    headers = WcMessage()
    headers['Content-Type'] = "text/html"
    attrs = get_filterattrs(fname, [FILTER_RESPONSE_MODIFY], headers=headers)
    filtered = ""
    data = f.read(2048)
    while data:
        print >>sys.stderr, "Test: data", len(data)
        try:
            filtered += applyfilter(FILTER_RESPONSE_MODIFY, data, 'filter',
                                    attrs)
        except FilterException, msg:
            print >>sys.stderr, "Test: exception:", msg
            pass
        data = f.read(2048)
    print >>sys.stderr, "Test: finishing"
    i = 1
    while True:
        print >>sys.stderr, "Test: finish", i
        try:
            filtered += applyfilter(FILTER_RESPONSE_MODIFY, "", 'finish',
                                    attrs)
            break
        except FilterException, msg:
            print >>sys.stderr, "Test: finish: exception:", msg
            proxy_poll(timeout=max(0, run_timers()))
        i += 1
        if i==200:
            # background downloading if javascript is too slow
            print >>sys.stderr, "Test: oooooops"
            break
    print "Filtered:", filtered


if __name__=='__main__':
    _main()
