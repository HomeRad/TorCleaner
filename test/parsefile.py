#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.getcwd())
from wc.parser.htmllib import HtmlPrinter

def _main():
    data = file(sys.argv[1]).read()
    #data = """<a href=/ >"""
    p = HtmlPrinter()
    p.feed(data)
    p.flush()

if __name__=='__main__':
    _main()
