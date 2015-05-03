# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Test javascript filtering.
"""

import unittest
import os
import wc.configuration
from wc.proxy.mainloop import proxy_poll
from wc.proxy.timer import run_timers
from wc.http.header import WcMessage
from wc.filter import FilterException
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY


class TestRewriteScript(unittest.TestCase):
    """
    All these tests work with the test filter configuration.
    If you change any of the *.zap filter configs, tests can fail...
    """

    def setUp(self):
        confdir = os.path.join("test", "config")
        wc.configuration.init(confdir=confdir)
        wc.configuration.config['filters'] = ['HtmlRewriter',]
        wc.configuration.config.init_filter_modules()
        wc.proxy.dns_lookups.init_resolver()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/html"
        self.attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY],
                                     serverheaders=self.headers,
                                     headers=self.headers)

    def filt(self, data, result):
        filtered = ""
        try:
            filtered += applyfilter(STAGE_RESPONSE_MODIFY, data, 'filter', self.attrs)
        except FilterException:
            pass
        i = 1
        while 1:
            try:
                filtered += applyfilter(STAGE_RESPONSE_MODIFY, "", 'finish', self.attrs)
                break
            except FilterException:
                proxy_poll(timeout=max(0, run_timers()))
            i+=1
            if i==100:
                # background downloading of javascript is too slow
                raise FilterException("Slow")
        self.assertEqual(filtered, result)

    def testEmpty(self):
        self.filt(
"""<script language="JavaScript">

</script>""", "")

    def testStandard(self):
        self.filt(
"""<script type="text/javascript" defer>
<!-- Hide code for older browsers...
// window instance
w = self;

function finish() {
    w.defaultStatus = "";
}

function get_date() {
    var d = new Date();
    today = "" + d.getDate() +"."+ (d.getMonth()+ 1) + "." + d.getYear();
    return today;
}

function get_time() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = now.getMinutes();
    var seconds = now.getSeconds();
    var timeValue = "" + hours;
    timeValue += ((minutes < 10) ? ":0" : ":") + minutes;
    timeValue += ((seconds < 10) ? ":0" : ":") + seconds;
    return timeValue;
}

function display() {
    message = "Calvin wünscht angenehmes Surfen am " + get_date() + " um " + get_time () + ".";
    w.defaultStatus = message;
}
// end of script. -->
</script>""",
"""<script type="text/javascript" defer>//<![CDATA[
// window instance
w = self;
function finish() {
    w.defaultStatus = "";
}
function get_date() {
    var d = new Date();
    today = "" + d.getDate() +"."+ (d.getMonth()+ 1) + "." + d.getYear();
    return today;
}
function get_time() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = now.getMinutes();
    var seconds = now.getSeconds();
    var timeValue = "" + hours;
    timeValue += ((minutes < 10) ? ":0" : ":") + minutes;
    timeValue += ((seconds < 10) ? ":0" : ":") + seconds;
    return timeValue;
}
function display() {
    message = "Calvin wünscht angenehmes Surfen am " + get_date() + " um " + get_time () + ".";
    w.defaultStatus = message;
}//]]></script>""")

    def testRecursion1(self):
        self.filt(
"""<script language="JavaScript">
<!--
document.write('foo');
//-->
</script>
      </td>
   </tr>
</table>""",
"""foo
      </td>
   </tr>
</table>""")

    def testRecursion3(self):
        self.filt(
"""<script language="JavaScript">
<!--
document.write('<SCR'+'IPT LANGUAGE="JavaScript1.1">' );
document.write('a=0;');
document.write('</SCR'+'IPT>');
//-->
</script>
      </td>
   </tr>
</table>""",
"""<script language="JavaScript1.1">//<![CDATA[
a=0;//]]></script>
      </td>
   </tr>
</table>""")

    def testScriptSrc4(self):
        self.filt(
"""<script src="http://imadoofus.org/notfound.js">
/* this should not be here **/
</script>""",
"""<!-- error fetching script from u\'http://imadoofus.org/notfound.js\' -->
<script type="text/javascript">//<![CDATA[
// error fetching script from u'http://imadoofus.org/notfound.js'//]]></script>""")

    def testScriptSrc5(self):
        self.filt(
"""<script src="file:///C:/Progra~1/1.js"></script>

</html>""",
"""

</html>""")

    def testCommentQuoting(self):
        self.filt(
"""<script language="JavaScript">
function a () {
}
</script>""",
"""<script language="JavaScript">//<![CDATA[
function a () {
}//]]></script>""")
        self.filt(
"""<script language="JavaScript">
<!--
function a () {
}//-->
</script>""",
"""<script language="JavaScript">//<![CDATA[
function a () {
}//]]></script>""")
        self.filt(
"""<script language="JavaScript">
<!--
function a () {
}
-->
</script>""",
"""<script language="JavaScript">//<![CDATA[
function a () {
}//]]></script>""")

    def testFlash(self):
        self.filt(
"""<script language="JavaScript1.1">
<!--
var words = navigator.plugins["Shockwave Flash"].description.split(" ");
//-->
</script>""",
"""<script language="JavaScript1.1">//<![CDATA[
var words = navigator.plugins["Shockwave Flash"].description.split(" ");//]]></script>""")

    def testHostname(self):
        self.filt(
"""<script language="JavaScript1.1">
<!--
var v1 = document.location.hostname;
var v2 = location.hostname;
//-->
</script>""",
"""<script language="JavaScript1.1">//<![CDATA[
var v1 = document.location.hostname;
var v2 = location.hostname;//]]></script>""")

    def testNonScript(self):
        self.filt(
"""<script language="VBScript">
<!--
tooooooot.
//-->
</script>""",
"""<script language="VBScript">
<!--
tooooooot.
//-->
</script>""")

    def testScriptError(self):
        self.filt(
"""<script language="JavaScript1.1">
<!--
tooooooot.
//-->
</script>""",
"""<script language="JavaScript1.1">//<![CDATA[
tooooooot.//]]></script>""")

    def testCommentQuoting2(self):
        self.filt(
"""<script>
<!-- hui
a = 0
// bui -->
</script>""",
"""<script>//<![CDATA[
a = 0//]]></script>""")

    def testCommentQuoting3(self):
        self.filt(
"""<script>
<!-- hui
a = 0; b = a--;
// bui -->
</script>""",
"""<script>//<![CDATA[
a = 0; b = a--;//]]></script>""")

    def testCommentQuoting4(self):
        self.filt(
"""<script>
<!-- hui
a = "-->";
// bui -->
</script>""",
"""<script>//<![CDATA[
a = "-->";//]]></script>""")

    def testPopup1(self):
        self.filt(
"""<script>
function a () {
    window.open();
}
a();
</script>""", "")

    def testPopup2(self):
        self.filt(
"""<script>
function a () {
    alert("bla");
}
a();
</script>""", "")

    def testFilter(self):
        self.filt("""<script src="http://ivwbox.de"></script>""", "")

    def test_quoting1(self):
        self.filt("""<script>
function a() {
    alert("This is not a </script>!");
}
</script>""", """<script>//<![CDATA[
function a() {
    alert("This is not a </scr"+"ipt>!");
}//]]></script>""")

    def test_quoting2(self):
        self.filt("""<script>
/* </script>blubb */
</script>""", """<script>//<![CDATA[
/* blubb *///]]></script>""")
