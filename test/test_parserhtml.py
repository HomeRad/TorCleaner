import os
from wc.parser.htmllib import HtmlPrinter

def _test():
    p = HtmlPrinter()
    path = "test/html"
    for f in ["1.html", "2.html", "3.html"]:
        file = os.path.join(path, f)
        print "parsing", f
        p.feed(open(file).read())
        p.flush()
        p.reset()

_test()
