#!/usr/bin/python2.3
import sys, os, stat, mimetypes
sys.path.insert(0, os.getcwd())

def _main():
    f = sys.argv[1]
    data = file(f).read()
    import wc, time
    wc.DebugLevel = 3
    wc.config = wc.Configuration()
    wc.config['filters'] = ['ImageReducer']
    wc.config.init_filter_modules()
    headers = {
        'Content-Type': mimetypes.guess_type(f)[0],
        'Content-Size': os.stat(f)[stat.ST_SIZE],
    }
    attrs = wc.filter.initStateObjects(headers=headers, url=f)
    filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
           data, 'finish', attrs)
    print filtered,


if __name__=='__main__':
    _main()
