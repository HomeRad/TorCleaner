#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def main ():
    """USAGE: test/run.sh test/imagereduce.py image.{gif,png,..} > reduced.jpg
    """
    import sys, os, stat, mimetypes
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    f = sys.argv[1]
    data = file(f).read()
    from test import initlog
    initlog("test/logging.conf")
    import wc
    wc.config = wc.Configuration()
    wc.config['filters'] = ['ImageReducer']
    wc.config.init_filter_modules()
    from wc.proxy.Headers import WcMessage
    headers = WcMessage(StringIO('')
    headers['Content-Type'] = mimetypes.guess_type(f)[0]
    headers['Content-Size'] = os.stat(f)[stat.ST_SIZE]
    from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
    attrs = get_filterattrs(f, [FILTER_RESPONSE_MODIFY], headers=headers)
    filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
    print filtered,


if __name__=='__main__':
    main()
