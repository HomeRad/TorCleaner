# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

import unittest, os
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.log import initlog

class TestJavaScript (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.config = wc.Configuration()
        wc.config['filters'] = ['Rewriter']
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))


    def filt (self, data, result, name=""):
        attrs = get_filterattrs(name, [FILTER_RESPONSE_MODIFY])
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)


    def testClosingTag (self):
        self.filt("""<a CONTENT="Andrew McDonald <andrew@mcdonald.org.uk>">""",
                  """<a content="Andrew McDonald <andrew@mcdonald.org.uk>">""")


    def testMetaRefresh (self):
        self.filt("""<META http-equiv="refresh">""",
                  """<meta http-equiv="refresh">""")


    def testMetaReFresh (self):
        self.filt("""<meta http-equiv="ReFresh">""",
                  """<meta http-equiv="ReFresh">""")


    def testMetaRefrish (self):
        self.filt("""<meta http-equiv="Refrish">""",
                  """<meta http-equiv="Refrish">""")


    def testShortcutIcon (self):
        self.filt("""<link rel="shortcut icon"></link>""", "")


    def testJavascriptInBody (self):
        self.filt("""<body onload="hulla();" onunload="holla();">""",
                  """<body onload="hulla();">""")


    def testAdvertLinks (self):
        self.filt("""<a href="http://www.doubleclick.net/">...</a>""", "")
        self.filt("""<a href="http://ads.freshmeat.net/">...</a>""", "")


    def testBlink (self):
        self.filt("""<blink>blinking text</blink>""",
                  """<b>blinking text</b>""")


    def testNoscript (self):
        self.filt("""<noscript>Kein Javascript</noscript>""", "")


    def _testErotic (self):
        self.filt("""<a href="http://playboy.com/issue/">blubba</a>""",
                  """<a href="http://www.calvinandhobbes.com/">blubba</a>""")


    def testRedirect (self):
        self.filt("""<a href="http://www.fileleech.com/dl/?filepath=http://www.counter-strike.de/downloads/ghl10full.exe&download=1">CS 1.0</a>""",
                  """<a href="http://www.counter-strike.de/downloads/ghl10full.exe">CS 1.0</a>""")


    def testEntity (self):
        self.filt("""Hallo Ernie & Bert, was geht?""",
                  """Hallo Ernie & Bert, was geht?""")


    def testEntities (self):
        self.filt("""Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;äöü?""",
                  """Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;äöü?""")


    def testTrackerImage (self):
        self.filt("""<img src="blubb" width="1" height="1">""", "")


    def testAdlog (self):
        self.filt("""<a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'></a>""", "")


    def testStartTag (self):
        """unquoted attribute ending with slash"""
        self.filt("""<a href=http://www/>link</a>""",
                  """<a href="http://www/">link</a>""")


    def testUncommonAttrChars (self):
        self.filt("""<a href="123$456">abc</a>""",
                  """<a href="123$456">abc</a>""")


    def testInputType (self):
        """IE crash"""
        self.filt("""<input type >""",
                  """<input>""")


    def testFielsetStyle (self):
        """Mozilla crash"""
        self.filt("""<fieldset style="position:absolute;">""",
                  """<fieldset>""")


    def testHrAlign (self):
        """IE crash"""
        self.filt("""<hr align="123456789 123456789 123456789 123456789 123456789 123456789">""",
                  """<hr>""")


    def testObjectType (self):
        """IE crash"""
        self.filt("""<object type="////////////////////////////////////////////////////////////AAAAA">""",
                  """<object type="/AAAAA">""")


    def testHrefPercent (self):
        """Opera crash"""
        self.filt("""<a href="file://server%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%text"></a>""",
                  """<a></a>""")


if __name__ == '__main__':
    unittest.main()
