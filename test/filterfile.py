#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())


def _main():
    f = sys.argv[1]
    data = file(f).read()
    import wc, time
    # set debug level
    wc.set_debuglevel(wc.NIGHTMARE)
    wc.config = wc.Configuration()
    # debug level could be reset, so set it again
    wc.set_debuglevel(wc.NIGHTMARE)
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    from wc.proxy import proxy_poll, run_timers
    from wc.filter import FilterException
    attrs = wc.filter.initStateObjects(url=f)
    filtered = ""
    i = 1
    while 1:
        try:
            filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                                             data, 'finish', attrs)
            break
        except FilterException, msg:
            print "Test: finish: exception:", msg
            data = ""
            proxy_poll(timeout=max(0, run_timers()))
        i+=1
        if i==99:
            print "Test: oooooops"
            break
    print filtered


if __name__=='__main__':
    _main()
