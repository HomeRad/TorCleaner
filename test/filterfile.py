#!/usr/bin/python2.3
import sys, os
sys.path.insert(0, os.getcwd())


def _main():
    fname = sys.argv[1]
    if fname=="-":
        f = sys.stdin
    else:
        f = file(fname)
    import wc, time
    from wc.log import initlog
    initlog("test/logging.conf")
    wc.config = wc.Configuration()
    # set debug level
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    from wc.proxy import proxy_poll, run_timers
    from wc.filter import FilterException
    attrs = wc.filter.initStateObjects(url=fname)
    filtered = ""
    data = f.read(1024)
    while data:
        try:
            filtered += wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                                              data, 'filter', attrs)
        except FilterException, msg:
            pass
        data = f.read(1024)
    i = 1
    while 1:
        print >>sys.stderr, "Test: finish", i
        try:
            filtered += wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                                             "", 'finish', attrs)
            break
        except FilterException, msg:
            print >>sys.stderr, "Test: finish: exception:", msg
            proxy_poll(timeout=max(0, run_timers()))
        i+=1
        if i==200:
            # background downloading if javascript is too slow
            print "Test: oooooops"
            break
    print filtered


if __name__=='__main__':
    _main()
