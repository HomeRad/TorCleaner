#!/usr/bin/env python
import sys
sys.path.insert(0, ".")
from wc.parser.htmllib import HtmlPrinter

def _main():
    file = sys.argv[1]
    data = open(file).read()
    p = HtmlPrinter()
    for c in data:
        p.feed(c)
    p.flush()


if __name__=='__main__':
    _main()
