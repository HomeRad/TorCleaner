#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
import sys
try:
    from wc.parser.htmllib import HtmlPrinter
except ImportError:
    print "using local development version"
    import os
    sys.path.insert(0, os.getcwd())
    from wc.parser.htmllib import HtmlPrinter

def _main():
    if len(sys.argv)==0 or sys.argv[1]=='-':
        f = sys.stdin
    else:
        f = file(sys.argv[1])
    p = HtmlPrinter()
    p.debug(1)
    data = f.read(1024)
    while data:
        p.feed(data)
        data = f.read(1024)
    p.flush()

if __name__=='__main__':
    _main()
