# -*- coding: iso-8859-1 -*-
from wc.parser.htmllib import HtmlPrinter
from wc.parser import htmlsax
import sys
sys.stderr = sys.stdout

tests = (
    # start tags
    """<a b="c">""",
    """<a b='c'>""",
    """<a b=c">""",
    """<a b="c>""",
    """<a b="">""",
    """<a b=''>""",
    """<a b=>""",
    """<a =c>""",
    """<a =>""",
    """<a b= "c">""",
    """<a b ="c">""",
    """<a b = "c">""",
    """<a >""",
    """< a>""",
    """< a >""",
    """<>""",
    """< >""",
    # reduce test
    """<a b="c"><""",
    """d>""",
    # numbers in tag
    """<h1>bla</h1>""",
    # more start tags
    """<a b=c"><a b="c">""",
    """<a b="c><a b="c">""",
    """<a b=/c/></a><br>""",
    """<br/>""",
    """<a b="50%"><br>""",
    # comments
    """<!---->""",
    """<!----->""",
    """<!------>""",
    """<!------->""",
    """<!---- >""",
    """<!-- -->""",
    """<!-- -- >""",
    """<!---- />-->""",
    # end tags
    """</a>""",
    """</ a>""",
    """</ a >""",
    """</a >""",
    """< / a>""", # invalid (is start tag)
    """< /a>""", # invalid (is start tag)
    """</td <td a="b" >""", # missing > in end tag
    # start and end tag
    """<a/>""",
    # declaration tags
    """<!DOCtype adrbook SYSTEM "adrbook.dtd">""",
    # misc
    """<?xmL version="1.0" encoding="latin1"?>""",
    # javascript
    """<script >\n</script>""",
    """<sCrIpt lang="a">bla </a> fasel</scripT>""",
    # line continuation (Dr. Fun webpage)
    "<img bo\\\nrder=0 >",
    # href with $
    """<a href="123$456">""",
    # quoting
    """<a href=/>""",
    """<a href="'">""",
    """<a href='"'>""",
    # entities
    """<a href="&#109;ailto:">"""
)

flushtests = (
    "<",
    "<a",
    "<!a",
    "<?a",
)

def _test():
    print "============ syntax tests ============="
    p = htmlsax.parser(HtmlPrinter())
    for t in tests:
        print "HTML", `t`
        p.feed(t)
        p.flush()
        p.reset()
    print "======== sequential feed tests ========="
    for t in tests:
        print "HTML", `t`
        for c in t:
            p.feed(c)
        p.flush()
        p.reset()
    print "===== subsequent interwoven parsing ===="
    p1 = htmlsax.parser(HtmlPrinter())
    p.feed("<")
    p1.feed("<")
    p.feed("ht")
    p1.feed("ht")
    p.feed("ml")
    p1.feed("ml")
    p.feed(">")
    p1.feed(">")
    p.flush()
    p1.flush()
    p.reset()
    p1.reset()
    print "============= reset test ==============="
    p.feed("<")
    p.reset()
    p.feed(">")
    p.flush()
    p.reset()
    print "============ flush tests ==============="
    for t in flushtests:
        print "FLUSH test "+t
        p.reset()
        p.feed(t)
        p.flush()
    p.reset()
    print "finished"

_test()
sys.stderr = sys.__stderr__
