import os
from wc.parser.htmllib import HtmlPrinter

def _test():
    p = HtmlPrinter()
    path = "test/html"
    for f in os.listdir(path):
        file = os.path.join(path, f)
        if not os.path.isfile(file): continue
        print "parsing", f
        p.feed(open(file).read())
        p.flush()
        p.reset()

_test()
