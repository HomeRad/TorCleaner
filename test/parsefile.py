#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-

def _main ():
    """USAGE: test/run.sh test/parsefile.py test.html"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    if sys.argv[1]=='-':
        f = sys.stdin
    else:
        f = file(sys.argv[1])
    from wc.parser.htmllib import HtmlPrettyPrinter
    from wc.parser import htmlsax
    p = htmlsax.parser(HtmlPrettyPrinter())
    #p.debug(1)
    data = f.read(1024)
    while data:
        p.feed(data)
        data = f.read(1024)
    p.flush()

if __name__=='__main__':
    _main()
