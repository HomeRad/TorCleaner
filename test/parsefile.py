#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())
from wc.parser.htmllib import HtmlPrinter

def _main():
    fname = sys.argv[1]
    if fname=='-':
        f = sys.stdin
    else:
        f = file(fname)
    p = HtmlPrinter()
    data = f.read(1024)
    while data:
        p.feed(data)
        data = f.read(1024)
    p.flush()

if __name__=='__main__':
    _main()
