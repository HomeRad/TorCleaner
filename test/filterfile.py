#!/usr/bin/env python
import sys
sys.path.insert(0, ".")

def _main():
    file = sys.argv[1]
    data = open(file).read()
    import wc, time
    wc.DebugLevel = 0
    wc.config['filters'] = ['Rewriter']
    wc.config.init_filter_modules()
    attrs = wc.filter.initStateObjects()
    filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
           data, 'finish', attrs)
    print filtered


if __name__=='__main__':
    _main()
