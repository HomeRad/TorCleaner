#!/usr/bin/python2.3
import sys
try:
    from wc.parser.htmllib import HtmlPrinter
    raise SystemExit("Global WebCleaner installation found")
except ImportError:
    import os
    sys.path.insert(0, os.getcwd())
    from wc.parser.htmllib import HtmlPrinter

def _main():
    fname = sys.argv[1]
    if fname=='-':
        f = sys.stdin
    else:
        f = file(fname)
    p = HtmlPrinter()
    p.debug(1)
    data = f.read(1024)
    while data:
        p.feed(data)
        data = f.read(1024)
    p.flush()

if __name__=='__main__':
    _main()
