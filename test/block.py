#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
import sys
import wc


def _main():
    _url = sys.argv[1]
    from wc.log import *
    initlog("test/logging.conf")
    wc.config = wc.Configuration()
    wc.config['filters'] = ['Blocker',]
    wc.config.init_filter_modules()
    attrs = wc.filter.initStateObjects(url=_url)
    filtered = \
       wc.filter.applyfilter(wc.filter.FILTER_REQUEST, _url, 'finish', attrs)
    print filtered

if __name__=='__main__':
    _main()
