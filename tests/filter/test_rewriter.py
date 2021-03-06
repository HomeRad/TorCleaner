# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Test script to test filtering.
"""

import unittest
import os
import wc.configuration
import wc.filter.html.JSFilter
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY
from wc.http.header import WcMessage


class TestRewriter(unittest.TestCase):
    """
    All these tests work with a _default_ filter configuration.
    If you change any of the *.zap filter configs, tests can fail.
    """

    def setUp(self):
        logfile = os.path.join(wc.InstallData, "test", "logging.conf")
        wc.initlog(logfile, filelogs=False)
        confdir = os.path.join("test", "config")
        wc.configuration.init(confdir=confdir)
        wc.configuration.config['filters'] = ['HtmlRewriter']
        wc.configuration.config.init_filter_modules()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/html"

    def filt(self, data, result, url=""):
        """
        Filter specified data, expect result. Call this only once per test!
        """
        self.attrs = get_filterattrs(url, "localhost",
             [STAGE_RESPONSE_MODIFY], serverheaders=self.headers,
             headers=self.headers)
        filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', self.attrs)
        self.assertEqual(filtered, result)

    def testClosingTag(self):
        """
        Close tag in attribute value.
        """
        self.filt("""<a CONTENT="Andrew McDonald <andrew@mcdonald.org.uk>">""",
                  """<a content="Andrew McDonald <andrew@mcdonald.org.uk>">""")

    def testMetaRefresh(self):
        """
        Meta refresh.
        """
        self.filt("""<META http-equiv="refresh">""",
                  """<meta http-equiv="refresh">""")

    def testMetaRefresh2(self):
        """
        Meta reFresh.
        """
        self.filt("""<meta http-equiv="ReFresh">""",
                  """<meta http-equiv="ReFresh">""")

    def testMetaRefrish(self):
        """
        Meta refrish.
        """
        self.filt("""<meta http-equiv="Refrish">""",
                  """<meta http-equiv="Refrish">""")

    def testMetaRefresh3(self):
        """
        Javascript refresh.
        """
        self.filt("""<meta name="Refresh" """ +
                  """content="1;url=http://;url=javascript:alert('boo')">""",
                  """<meta name="Refresh">""")
        self.filt("""<meta http-equiv="Refresh" """ +
                  """content="1; url =http://;url=jaVaScrIpt:alert('boo')">""",
                  """<meta http-equiv="Refresh">""")

    def testShortcutIcon(self):
        """
        Shortcut icon.
        """
        self.filt("""<link rel="shortcut icon"></link>""", "")

    def testJavascriptInBody(self):
        """
        Onunload in body.
        """
        self.filt("""<body onload="hulla();" onunload="holla();">""",
                  """<body onload="hulla();">""")

    def testBodyPopup(self):
        for tag in wc.filter.html.JSFilter.js_event_attrs:
            self.filt("""<body %s="window.open();">""" % tag,
                  """<body>""")

    def testJavascriptError(self):
        self.filt("""<body onload="uru,guru">""",
                  """<body onload="uru,guru">""")

    def testAdvertLinks1(self):
        """
        Doubleclick advert.
        """
        self.filt("""<a href="http://www.doubleclick.net/">...</a>""", "")

    def testAdvertLinks2(self):
        """
        Freshmeat ad.
        """
        self.filt("""<a href="http://ads.freshmeat.net/">...</a>""", "")

    def testBlink(self):
        """
        Blinking text.
        """
        self.filt("""<blink>blinking text</blink>""",
                  """<b>blinking text</b>""")

    def testNoscript(self):
        """
        Remove noscript.
        """
        self.filt("""<noscript>Kein Javascript</noscript>""", "")

    def testRedirect(self):
        """
        Fileleech redirection.
        """
        self.filt("""<a href="http://www.fileleech.com/dl/?filepath=http://www.counter-strike.de/downloads/ghl10full.exe&download=1">CS 1.0</a>""",
                  """<a href="http://www.counter-strike.de/downloads/ghl10full.exe">CS 1.0</a>""")

    def testEntity(self):
        """
        Lone entity quoting.
        """
        self.filt("""Hallo Ernie & Bert, was geht?""",
                  """Hallo Ernie & Bert, was geht?""")

    def testEntities(self):
        """
        Entity quoting.
        """
        self.filt("""Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;���?""",
                  """Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;���?""")

    def testCharset(self):
        """
        Non-ascii characters.
        """
        self.filt("""<�zg�r> fahr </langsamer> ������{""",
                  """<�zg�r> fahr </langsamer> ������{""")

    def testTrackerImage(self):
        """
        1x1 tracker image.
        """
        self.filt("""<img src="blubb" width="1" height="1">""", "")

    def testAdlog(self):
        """
        Adlog.pl advert.
        """
        self.filt("""<a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'></a>""",
                  "")

    def testStartTag(self):
        """
        Unquoted attribute ending with slash.
        """
        self.filt("""<a href=http://www/>link</a>""",
                  """<a href="http://www/">link</a>""")

    def testUncommonAttrChars(self):
        """
        Uncommon attribute characters.
        """
        self.filt("""<a href="123$456">abc</a>""",
                  """<a href="123$456">abc</a>""")

    def testInputType(self):
        """
        IE input type crash.
        """
        self.filt("""<input type >""",
                  """<input>""")

    def testFielsetStyle(self):
        """
        Mozilla fieldset crash.
        """
        self.filt("""<fieldset style="position:absolute;">""",
                  """<fieldset>""")

    def testHrAlign(self):
        """
        IE crash.
        """
        self.filt("""<hr align="123456789 123456789 123456789 123456789 123456789 123456789">""",
                  """<hr>""")

    def testObjectType(self):
        """
        IE object type crash.
        """
        # To avoid virus alarms we obfuscate the exploit URL.
        # This code is harmless.
        slashes = "/" * 60
        self.filt("""<object type="/%sAAAAA">""" % slashes,
                  """<object type="/AAAAA">""")

    def testHrefPercent(self):
        """
        Opera file crash.
        """
        # To avoid virus alarms we obfuscate the exploit URL.
        # This code is harmless.
        percents = "%" * 178
        self.filt("""<a href="file://server%stext"></a>""" % percents,
                  """<a></a>""")

    def testHrefDashes(self):
        """
        Mozilla Firefox dashes-in-hostname crash.
        """
        dashes = "-" * 44
        self.filt("""<a href=https:%s >""" % dashes,
                  """<a>""")

    def testITSVuln(self):
        """
        Microsoft Internet Explorer ITS Protocol Zone Bypass Vulnerability.
        """
        # To avoid virus alarms we obfuscate the exploit URL.
        # This code is harmless.
        data_url = "&#109;s-its:mhtml:file://"+ \
                   "C:\\foo.mht!${PATH}/"+ \
                   "EXPLOIT.CHM::"+ \
                   "/exploit.htm"
        self.filt("""<object data="%s">""" % data_url,
                  """<object data="ms-its:mhtml:file:/C:/foo.mht">""")

    def testImgWidthHeight(self):
        for tag in ("width", "height"):
            self.filt("""<img %s="9999">""" % tag,
                      """<img %s="9999">""" % tag)
            self.filt("""<img %s="12345">""" % tag,
                      """<img>""")

    def testFirelinking(self):
        self.filt("""<link rel="icon " href= " javascript:void()">""",
                  """<link rel="icon ">""")

    def testStartEndTag(self):
        self.filt("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<base href="bla"/>
""",
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<base href="bla"/>
""")

    # sourcetext and parsererror tags hang Mozilla browsers
    # See https://bugzilla.mozilla.org/show_bug.cgi?id=210658
    def testSourcetext(self):
        self.filt("""<html><body><strong>Mozilla<sourcetext></body></html>""",
                  """<html><body><strong>Mozilla</body></html>""")

    def testParsererror(self):
        self.filt("""<html><body><p><parsererror></parsererror></p></body></html>""",
                  """<html><body><p></p></body></html>""")

    def testAppletHspace(self):
        self.filt("""<frameset><frame src="aaa"><embed name="sp" style><applet hspace="file:\\\\">""",
                  """<frameset><frame src="aaa"><embed name="sp" style><applet>""")

    def testEnclosing(self):
        self.filt("""<table width="25%"><a href="/pagead/iclk?sa=l&ai=B"></table>""",
                  "", url="www.google.com")

    def test_script(self):
        self.filt("""<script src="https://localhost/1.js" type="text/javascript"></script>""",
                  """<script src="https://localhost/1.js" type="text/javascript"></script>""")
        self.filt("""<script type="text/javascript"></script>""",
                  """""")
        self.filt("""<script type="text/javascript">window.status='';a=1</script>""",
                  """<script type="text/javascript">a=1</script>""")

    def test_ie_jshandler_crash(self):
        # multiple attributes with same name should be merged
        bork = ' onclick="bork"'
        html = '<html><body><img src="foo.jpg"><foo%s><p>Hello'
        self.filt(html % (bork * 1500), html % bork)

    def test_alt_title(self):
        self.filt("""<img alt="">""", """<img alt="" title="">""")

    def test_ie_object_crash(self):
        # nested object tag level is restricted to 3
        obj_tag = "<object>"
        self.filt(obj_tag * 4, obj_tag * 3)
