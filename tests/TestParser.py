# -*- coding: iso-8859-1 -*-
from wc.parser.htmllib import HtmlPrettyPrinter
from wc.parser import htmlsax, resolve_entities
from cStringIO import StringIO

import unittest
from wc import ip


class TestParser (unittest.TestCase):
    def setUp (self):
        # list of tuples (<test pattern>, <expected parse output>)
        self.htmltests = (
        # start tags
        ("""<a  b="c">""", """<a b="c">"""),
        ("""<a  b='c'>""", """<a b="c">"""),
        ("""<a  b=c">""", """<a b="c">"""),
        ("""<a  b=c'>""", """<a b="c">"""),
        ("""<a  b="c>""", """<a  b="c>"""),
        ("""<a  b="">""", """<a b="">"""),
        ("""<a  b=''>""", """<a b="">"""),
        ("""<a  b=>""", """<a b="">"""),
        ("""<a  =c>""", """<a c>"""),
        ("""<a  =>""", """<a>"""),
        #XXX("""<a b= "c">""", """<a b="c">"""),
        ("""<a  b ="c">""", """<a b="c">"""),
        #XXX("""<a b = "c">""", """<a b="c">"""),
        ("""<a >""", """<a>"""),
        ("""< a>""", """<a>"""),
        ("""< a >""", """<a>"""),
        ("""<>""", """<>"""),
        ("""< >""", """< >"""),
        # reduce test
        ("""<a  b="c"><""", """<a b="c"><"""),
        ("""d>""", """d>"""),
        # numbers in tag
        ("""<h1>bla</h1>""", """<h1>bla</h1>"""),
        # more start tags
        ("""<a  b=c"><a b="c">""", """<a b="c"><a b="c">"""),
        ("""<a  b="c><a b="c">""", """<a b="c><a b=" c>"""),
        ("""<a  b=/c/></a><br>""", """<a b="/c/"></a><br>"""),
        ("""<br/>""", """<br>"""),
        ("""<a  b="50%"><br>""", """<a b="50%"><br>"""),
        # comments
        ("""<!---->""", """<!---->"""),
        ("""<!----->""", """<!----->"""),
        ("""<!------>""", """<!------>"""),
        ("""<!------->""", """<!------->"""),
        #XXX("""<!---- >""", """<!---- >"""),
        ("""<!-- -->""", """<!-- -->"""),
        #XXX("""<!-- -- >""", """<!-- -- >"""),
        ("""<!---- />-->""", """<!---- />-->"""),
        # end tags
        ("""</a>""", """</a>"""),
        ("""</ a>""", """</a>"""),
        ("""</ a >""", """</a>"""),
        ("""</a >""", """</a>"""),
        ("""< / a>""", """</a>"""),
        ("""< /a>""", """</a>"""),
        # missing > in end tag
        ("""</td <td  a="b" >""", """</td><td a="b">"""),
        # start and end tag
        ("""<a/>""", """<a></a>"""),
        # declaration tags
        ("""<!DOCtype adrbook SYSTEM "adrbook.dtd">""", """<!DOCTYPE adrbook SYSTEM "adrbook.dtd">"""),
        # misc
        ("""<?xmL version="1.0" encoding="latin1"?>""", """<?xmL version="1.0" encoding="latin1"?>"""),
        # javascript
        ("""<script >\n</script>""", """<script>\n</script>"""),
        ("""<sCrIpt lang="a">bla </a> fasel</scripT>""", """<script lang="a">bla </a> fasel</script>"""),
        # line continuation (Dr. Fun webpage)
        ("<img bo\\\nrder=0 >", """<img bo rder="0">"""),
        # href with $
        ("""<a href="123$456">""", """<a href="123$456">"""),
        # quoting
        ("""<a  href=/>""", """<a href="/">"""),
        ("""<a  href=>""", """<a href="">"""),
        ("""<a  href="'">""", """<a href="'">"""),
        ("""<a  href='"'>""", """<a href="&quot;">"""),
        ("""<a  href="bla" %]">""", """<a href="bla">"""),
        ("""<a  href=bla">""", """<a href="bla">"""),
        # entities
        ("""<a  href="&#109;ailto:">""", """<a href="mailto:">"""),
        )
        self.flushtests = (
            ("<", "<"),
            ("<a", "<a"),
            ("<!a", "<!a"),
            ("<?a", "<?a"),
        )
        self.htmlparser = htmlsax.parser()
        self.htmlparser2 = htmlsax.parser()


    def testParse (self):
        for _in, _out in self.htmltests:
            out = StringIO()
            self.htmlparser.handler = HtmlPrettyPrinter(out)
            self.htmlparser.feed(_in)
            self.htmlparser.flush()
            res = out.getvalue()
            self.assertEqual(res, _out)
            self.htmlparser.reset()


    def testFeed (self):
        for _in, _out in self.htmltests:
            out = StringIO()
            self.htmlparser.handler = HtmlPrettyPrinter(out)
            for c in _in:
                self.htmlparser.feed(c)
            self.htmlparser.flush()
            res = out.getvalue()
            self.assertEqual(res, _out)
            self.htmlparser.reset()


    def testInterwoven (self):
        for _in, _out in self.htmltests:
            out = StringIO()
            out2 = StringIO()
            self.htmlparser.handler = HtmlPrettyPrinter(out)
            self.htmlparser2.handler = HtmlPrettyPrinter(out2)
            for c in _in:
                self.htmlparser.feed(c)
                self.htmlparser2.feed(c)
            self.htmlparser.flush()
            self.htmlparser2.flush()
            res = out.getvalue()
            res2 = out2.getvalue()
            self.assertEqual(res, _out)
            self.assertEqual(res2, _out)
            self.htmlparser.reset()


    def testFlush (self):
        for _in, _out in self.flushtests:
            out = StringIO()
            self.htmlparser.handler = HtmlPrettyPrinter(out)
            self.htmlparser.feed(_in)
            self.htmlparser.flush()
            res = out.getvalue()
            self.assertEqual(res, _out)
            self.htmlparser.reset()


    def testEntities (self):
        for c in "abcdefghijklmnopqrstuvwxyz":
            self.assertEqual(resolve_entities("&#%d;"%ord(c)), c)


if __name__ == '__main__':
    unittest.main()
