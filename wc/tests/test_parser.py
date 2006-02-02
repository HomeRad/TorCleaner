# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Test html parsing.
"""

import wc.HtmlParser
import wc.HtmlParser.htmlsax
import wc.HtmlParser.htmllib
import tests
import cStringIO as StringIO
import unittest


# list of tuples
# (<test pattern>, <expected parse output>)
parsetests = [
    # start tags
    ("""<a  b="c" >""", """<a b="c">"""),
    ("""<a  b='c' >""", """<a b="c">"""),
    ("""<a  b=c" >""", """<a b="c">"""),
    ("""<a  b=c' >""", """<a b="c'">"""),
    ("""<a  b="c >""", """<a  b="c >"""),
    ("""<a  b="" >""", """<a b="">"""),
    ("""<a  b='' >""", """<a b="">"""),
    ("""<a  b=>""", """<a b="">"""),
    ("""<a  b= >""", """<a b="">"""),
    ("""<a  =c>""", """<a c>"""),
    ("""<a  =c >""", """<a c>"""),
    ("""<a  =>""", """<a>"""),
    ("""<a  = >""", """<a>"""),
    ("""<a  b= "c" >""", """<a b="c">"""),
    ("""<a  b ="c" >""", """<a b="c">"""),
    ("""<a  b = "c" >""", """<a b="c">"""),
    ("""<a >""", """<a>"""),
    ("""< a>""", """<a>"""),
    ("""< a >""", """<a>"""),
    ("""<>""", """<>"""),
    ("""< >""", """< >"""),
    ("""<a�>""", """<a>"""),
    ("""<a a�="b">""", """<a a="b">"""),
    ("""<a a="b�">""", """<a a="b&#228;">"""),
    # reduce test
    ("""<a  b="c"><""", """<a b="c"><"""),
    ("""d>""", """d>"""),
    # numbers in tag
    ("""<h1>bla</h1>""", """<h1>bla</h1>"""),
    # more start tags
    ("""<a  b=c"><a b="c">""", """<a b="c"><a b="c">"""),
    ("""<a  b=/c/></a><br>""", """<a b="/c/"></a><br>"""),
    ("""<br/>""", """<br>"""),
    ("""<a  b="50%"><br>""", """<a b="50%"><br>"""),
    # comments
    ("""<!---->< 1>""", """<!----><1>"""),
    ("""<!-- a - b -->< 2>""", """<!-- a - b --><2>"""),
    ("""<!----->< 3>""", """<!-----><3>"""),
    ("""<!------>< 4>""", """<!------><4>"""),
    ("""<!------->< 5>""", """<!-------><5>"""),
    ("""<!-- -->< 7>""", """<!-- --><7>"""),
    ("""<!---- />-->""", """<!---- />-->"""),
    ("""<!-- a-2 -->< 9>""", """<!-- a-2 --><9>"""),
    ("""<!-- --- -->< 10>""", """<!-- --- --><10>"""),
    # invalid comments
    ("""<!-- -- >< 8>""", """<!-- --><8>"""),
    ("""<!---- >< 6>""", """<!----><6>"""),
    ("""<!- blubb ->""", """<!-- blubb -->"""),
    ("""<! -- blubb -->""", """<!-- blubb -->"""),
    ("""<!-- blubb -- >""", """<!-- blubb -->"""),
    # end tags
    ("""</a>""", """</a>"""),
    ("""</ a>""", """</a>"""),
    ("""</ a >""", """</a>"""),
    ("""</a >""", """</a>"""),
    ("""< / a>""", """</a>"""),
    ("""< /a>""", """</a>"""),
    ("""</a�>""", """</a>"""),
    # start and end tag (HTML doctype assumed)
    ("""<a/>""", """<a/>"""),
    ("""<meta/>""", """<meta>"""),
    ("""<MetA/>""", """<meta>"""),
    # declaration tags
    ("""<!DOCtype adrbook SYSTEM "adrbook.dtd">""",
     """<!DOCTYPE adrbook SYSTEM "adrbook.dtd">"""),
    # misc
    ("""<?xmL version="1.0" encoding="latin1"?>""",
     """<?xmL version="1.0" encoding="latin1"?>"""),
    # javascript
    ("""<script >\n</script>""", """<script>\n</script>"""),
    ("""<sCrIpt lang="a">bla </a> fasel</scripT>""",
     """<script lang="a">bla </a> fasel</script>"""),
    # line continuation (Dr. Fun webpage)
    ("""<img bo\\\nrder=0 >""", """<img border="0">"""),
    ("""<img align="mid\\\ndle">""", """<img align="middle">"""),
    ("""<img align='mid\\\ndle'>""", """<img align="middle">"""),
    # href with $
    ("""<a href="123$456">""", """<a href="123$456">"""),
    # quoting
    ("""<a  href=/ >""", """<a href="/">"""),
    ("""<a  href= />""", """<a href="/">"""),
    ("""<a  href= >""", """<a href="">"""),
    ("""<a  href="'" >""", """<a href="'">"""),
    ("""<a  href='"' >""", """<a href="&quot;">"""),
    ("""<a  href="bla" %]" >""", """<a href="bla">"""),
    ("""<a  href=bla" >""", """<a href="bla">"""),
    ("""<a onmouseover=MM_swapImage('nav1','',"""\
     """'/images/dwnavpoint_over.gif',1);movein(this); b="c">""",
     """<a onmouseover="MM_swapImage('nav1','',"""\
     """'/images/dwnavpoint_over.gif',1);movein(this);" b="c">"""),
    ("""<a onClick=location.href('/index.htm') b="c">""",
     """<a onclick="location.href('/index.htm')" b="c">"""),
    # entity resolving
    ("""<a  href="&#6D;ailto:" >""", """<a href="ailto:">"""),
    ("""<a  href="&amp;ailto:" >""", """<a href="&amp;ailto:">"""),
    ("""<a  href="&amp;amp;ailto:" >""", """<a href="&amp;amp;ailto:">"""),
    ("""<a  href="&hulla;ailto:" >""", """<a href="ailto:">"""),
    ("""<a  href="&#109;ailto:" >""", """<a href="mailto:">"""),
    ("""<a  href="&#x6D;ailto:" >""", """<a href="mailto:">"""),
    # note that \u8156 is not valid encoding and therefore gets removed
    ("""<a  href="&#8156;ailto:" >""", """<a href="ailto:">"""),
    # non-ascii characters
    ("""<�zg�r> fahr </langsamer> ������{""",
     """<�zg�r> fahr </langsamer> ������{"""),
    # mailto link
    ("""<a  href=mailto:calvin@LocalHost?subject=Hallo&to=michi>1</a>""",
     """<a href="mailto:calvin@LocalHost?subject=Hallo&amp;to=michi">1</a>"""),
    # doctype XHTML
    ("""<!DOCTYPe html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><MeTa a="b"/>""",
     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><meta a="b"/>"""),
    # missing > in end tag
    ("""</td <td  a="b" >""", """</td><td a="b">"""),
    ("""</td<td  a="b" >""", """</td><td a="b">"""),
    # missing beginning quote
    ("""<td a=b">""", """<td a="b">"""),
    # missing end quote (XXX TODO)
    #("""<td a="b>\n""", """<td a="b">\n"""),
    #("""<td a="b></td>\na""", """<td a="b"></td>\na"""),
    #("""<a  b="c><a b="c>\n""", """<a b="c"><a b="c">\n"""),
    #("""<td a="b c="d"></td>\n""", """<td a="b" c="d"></td>\n"""),
]

flushtests = [
    ("<", "<"),
    ("<a", "<a"),
    ("<!a", "<!a"),
    ("<?a", "<?a"),
]


class TestParser (tests.StandardTest):
    """
    Test html parser.
    """

    def setUp (self):
        """
        Initialize two internal html parsers to be used for testing.
        """
        self.htmlparser = wc.HtmlParser.htmlsax.parser()
        self.htmlparser2 = wc.HtmlParser.htmlsax.parser()

    def test_parse (self):
        """
        Parse all test patterns in one go.
        """
        for _in, _out in parsetests:
            out = StringIO.StringIO()
            handler = wc.HtmlParser.htmllib.HtmlPrettyPrinter(out)
            self.htmlparser.handler = handler
            self.htmlparser.feed(_in)
            self.check_results(self.htmlparser, _in, _out, out)

    def check_results (self, htmlparser, _in, _out, out):
        """
        Check parse results.
        """
        htmlparser.flush()
        res = out.getvalue()
        msg = "Test error; in: %r, out: %r, expect: %r" % \
           (_in, res, _out)
        self.assertEqual(res, _out, msg=msg)
        htmlparser.reset()

    def test_feed (self):
        """
        Parse all test patterns sequentially.
        """
        for _in, _out in parsetests:
            out = StringIO.StringIO()
            handler = wc.HtmlParser.htmllib.HtmlPrettyPrinter(out)
            self.htmlparser.handler = handler
            for c in _in:
                self.htmlparser.feed(c)
            self.check_results(self.htmlparser, _in, _out, out)

    def test_interwoven (self):
        """
        Parse all test patterns on two parsers interwoven.
        """
        for _in, _out in parsetests:
            out = StringIO.StringIO()
            out2 = StringIO.StringIO()
            handler = wc.HtmlParser.htmllib.HtmlPrettyPrinter(out)
            self.htmlparser.handler = handler
            handler2 = wc.HtmlParser.htmllib.HtmlPrettyPrinter(out2)
            self.htmlparser2.handler = handler2
            for c in _in:
                self.htmlparser.feed(c)
                self.htmlparser2.feed(c)
            self.check_results(self.htmlparser, _in, _out, out)
            self.check_results(self.htmlparser2, _in, _out, out2)

    def test_flush (self):
        """
        Test parser flushing.
        """
        for _in, _out in flushtests:
            out = StringIO.StringIO()
            handler = wc.HtmlParser.htmllib.HtmlPrettyPrinter(out)
            self.htmlparser.handler = handler
            self.htmlparser.feed(_in)
            self.check_results(self.htmlparser, _in, _out, out)

    def test_entities (self):
        """
        Test entity resolving.
        """
        for c in "abcdefghijklmnopqrstuvwxyz":
            self.assertEqual(
                   wc.HtmlParser.resolve_entities("&#%d;" % ord(c)), c)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    return unittest.makeSuite(TestParser)


if __name__ == '__main__':
    unittest.main()
