#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main ():
    """USAGE: test/run.sh test/pfilterfile.py <.html file>"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    f = sys.argv[1]
    data = file(f).read()
    from test import initlog
    initlog("test/logging.conf")
    import wc
    wc.config = wc.Configuration()
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    attrs = wc.filter.initStateObjects(url=f)
    import profile
    profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, data, 'finish', attrs)",
                "filter.prof")


if __name__=='__main__':
    _main()
