#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())

def _main():
    f = sys.argv[1]
    data = file(f).read()
    import wc, time
    wc.set_debuglevel(wc.NIGHTMARE)
    wc.config = wc.Configuration()
    wc.set_debuglevel(wc.NIGHTMARE)
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    from wc.proxy import proxy_poll, run_timers
    from wc.filter import FilterException
    attrs = wc.filter.initStateObjects(url=f)
    i = 1
    while 1:
        try:
            filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
                   data, 'finish', attrs)
            print filtered
        except FilterException, msg:
            print msg
            data = ""
            proxy_poll(timeout=max(0, run_timers()))
        i+=1
        if i==5:
            break


if __name__=='__main__':
    _main()
