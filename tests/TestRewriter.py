# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

import unittest, os
import wc
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.log import initlog
from wc.proxy.Headers import WcMessage
from tests.StandardTest import StandardTest


class TestRewriter (StandardTest):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def init (self):
        super(TestRewriter, self).init()
        wc.config = wc.Configuration()
        wc.config['filters'] = ['Rewriter']
        wc.config.init_filter_modules()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/html"

    def setUp (self):
        self.attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY], headers=self.headers)

    def filt (self, data, result):
        """filter specified data, expect result. Call this only once per
           test!"""
        filtered = applyfilter(FILTER_RESPONSE_MODIFY, data, 'finish', self.attrs)
        self.assertEqual(filtered, result)

    def testClosingTag (self):
        """close tag in attribute value"""
        self.filt("""<a CONTENT="Andrew McDonald <andrew@mcdonald.org.uk>">""",
                  """<a content="Andrew McDonald <andrew@mcdonald.org.uk>">""")

    def testMetaRefresh (self):
        """meta refresh"""
        self.filt("""<META http-equiv="refresh">""",
                  """<meta http-equiv="refresh">""")

    def testMetaRefresh2 (self):
        """meta reFresh"""
        self.filt("""<meta http-equiv="ReFresh">""",
                  """<meta http-equiv="ReFresh">""")

    def testMetaRefrish (self):
        """meta refrish"""
        self.filt("""<meta http-equiv="Refrish">""",
                  """<meta http-equiv="Refrish">""")

    def testShortcutIcon (self):
        """shortcut icon"""
        self.filt("""<link rel="shortcut icon"></link>""", "")

    def testJavascriptInBody (self):
        """onunload in body"""
        self.filt("""<body onload="hulla();" onunload="holla();">""",
                  """<body onload="hulla();">""")

    def testAdvertLinks1 (self):
        """Doubleclick advert"""
        self.filt("""<a href="http://www.doubleclick.net/">...</a>""", "")

    def testAdvertLinks2 (self):
        """freshmeat ad"""
        self.filt("""<a href="http://ads.freshmeat.net/">...</a>""", "")

    def testBlink (self):
        """blinking text"""
        self.filt("""<blink>blinking text</blink>""",
                  """<b>blinking text</b>""")

    def testNoscript (self):
        """remove noscript"""
        self.filt("""<noscript>Kein Javascript</noscript>""", "")

    def XXXtestErotic (self):
        self.filt("""<a href="http://playboy.com/issue/">blubba</a>""",
                  """<a href="http://www.calvinandhobbes.com/">blubba</a>""")

    def testRedirect (self):
        """fileleech redirection"""
        self.filt("""<a href="http://www.fileleech.com/dl/?filepath=http://www.counter-strike.de/downloads/ghl10full.exe&download=1">CS 1.0</a>""",
                  """<a href="http://www.counter-strike.de/downloads/ghl10full.exe">CS 1.0</a>""")

    def testEntity (self):
        """lone entity quoting"""
        self.filt("""Hallo Ernie & Bert, was geht?""",
                  """Hallo Ernie & Bert, was geht?""")

    def testEntities (self):
        """entity quoting"""
        self.filt("""Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;äöü?""",
                  """Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;äöü?""")

    def testTrackerImage (self):
        """1x1 tracker image"""
        self.filt("""<img src="blubb" width="1" height="1">""", "")

    def testAdlog (self):
        """adlog.pl advert"""
        self.filt("""<a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'></a>""",
                  "")

    def testStartTag (self):
        """unquoted attribute ending with slash"""
        self.filt("""<a href=http://www/>link</a>""",
                  """<a href="http://www/">link</a>""")

    def testUncommonAttrChars (self):
        """uncommon attribute characters"""
        self.filt("""<a href="123$456">abc</a>""",
                  """<a href="123$456">abc</a>""")

    def testInputType (self):
        """IE input type crash"""
        self.filt("""<input type >""",
                  """<input>""")

    def testFielsetStyle (self):
        """Mozilla fieldset crash"""
        self.filt("""<fieldset style="position:absolute;">""",
                  """<fieldset>""")

    def testHrAlign (self):
        """IE crash"""
        self.filt("""<hr align="123456789 123456789 123456789 123456789 123456789 123456789">""",
                  """<hr>""")

    def testObjectType (self):
        """IE object type crash"""
        self.filt("""<object type="////////////////////////////////////////////////////////////AAAAA">""",
                  """<object type="/AAAAA">""")

    def testHrefPercent (self):
        """Opera file crash"""
        self.filt("""<a href="file://server%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%text"></a>""",
                  """<a></a>""")

    def testITSVuln (self):
        """Microsoft Internet Explorer ITS Protocol Zone Bypass Vulnerability"""
        self.filt("""<object data="&#109;s-its:mhtml:file://C:\\foo.mht!${PATH}/EXPLOIT.CHM::/exploit.htm">""",
                  """<object data="ms-its:mhtml:file:/C:/foo.mht">""")


if __name__ == '__main__':
    unittest.main(defaultTest='TestRewriter')
else:
    suite = unittest.makeSuite(TestRewriter, 'test')
