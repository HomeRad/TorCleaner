# -*- coding: iso-8859-1 -*-
import os
from wc.parser.htmllib import HtmlPrinter
from wc.parser import htmlsax

def _test():
    p = htmlsax.parser(HtmlPrinter())
    path = "test/html"
    for f in ["1.html", "2.html", "3.html"]:
        filename = os.path.join(path, f)
        print "parsing", f
        p.feed(file(filename).read())
        p.flush()
        p.reset()

_test()
