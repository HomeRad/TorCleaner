#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Parse HTML file with optional debugging.
"""

def _main(args):
    """
    USAGE: scripts/run.sh test/parsefile.py test.html.
    """
    if len(args) < 1:
        print _main.__doc__.strip()
        sys.exit(1)
    from wc.HtmlParser.htmllib import HtmlPrinter, HtmlPrettyPrinter
    if args[0] == "-p":
        klass = HtmlPrettyPrinter
        filename = args[1]
    else:
        klass = HtmlPrinter
        filename = args[0]
    if filename == '-':
        f = sys.stdin
    else:
        f = open(filename)
    from wc.HtmlParser import htmlsax
    p = htmlsax.parser(klass())
    p.debug(1)
    size = 1024
    #size = 1 # feed data to parser one character-at-a-time
    data = f.read(size)
    while data:
        p.feed(data)
        data = f.read(size)
    p.flush()

if __name__ == '__main__':
    import sys
    _main(sys.argv[1:])
