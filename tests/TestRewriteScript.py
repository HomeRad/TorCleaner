# -*- coding: iso-8859-1 -*-
"""test javascript filtering"""

import unittest
from test import disable_rating_rules
import wc
from wc.proxy import proxy_poll, run_timers
from wc.filter import FilterException
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
from wc.log import initlog


class TestJavaScript (unittest.TestCase):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def setUp (self):
        wc.config = wc.Configuration()
        disable_rating_rules(wc.config)
        wc.config['filters'] = ['Rewriter',]
        wc.config.init_filter_modules()
        initlog(os.path.join("test", "logging.conf"))


    def filt (self, data, result, name=""):
        attrs = get_filterattrs(name, [FILTER_RESPONSE_MODIFY])
        filtered = ""
        try:
            filtered += applyfilter(FILTER_RESPONSE_MODIFY, data, 'filter', attrs)
        except FilterException, msg:
            pass
        i = 1
        while 1:
            try:
                filtered += applyfilter(FILTER_RESPONSE_MODIFY, "", 'finish', attrs)
                break
            except FilterException, msg:
                proxy_poll(timeout=max(0, run_timers()))
            i+=1
            if i==100:
                # background downloading of javascript is too slow
                raise FilterException("Slow")
        self.assertEqual(filtered, result)


    def testEmpty (self):
        self.filt(
"""<script language="JavaScript">

</script>""", "")


    def testStandard (self):
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
"""<script type="text/javascript" defer>
<!--
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
//-->
</script>""")


    def testRecursion1 (self):
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


    def XXXtestRecursion2 (self):
        self.filt(
"""<script language="JavaScript">
<!--
document.write('<SCR'+'IPT LANGUAGE="JavaScript1.1" ' );
document.write('SRC="http://localhost/~calvin/test/2.js">');
document.write('</SCR'+'IPT>');
//-->
</script>
      </td>
   </tr>
</table>""",
"""
      </td>
   </tr>
</table>""")


    def XXXtestRecursion3 (self):
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
"""<script language="JavaScript1.1">
<!--
a=0;
//-->
</script>
      </td>
   </tr>
</table>""")


    def XXXtestScriptSrc1 (self):
        self.filt(
"""<script src="http://localhost/~calvin/test/1.js"></script>

</html>""",
"""
</html>""")


    def XXXtestScriptSrc2 (self):
        self.filt(
"""<script src="http://localhost/~calvin/test/1.js">
 
</script>

</html>""",
"""
</html>""")


    def XXXtestScriptSrc3 (self):
        """missing </script>"""
        self.filt(
"""<script src="http://localhost/~calvin/test/3.js"/>
<script type="JavaScript">
<!--
a = 1
// -->
</script>

</html>""",
"""XXX""")


    def XXXtestScriptSrc4 (self):
        self.filt(
"""<script src="http://localhost/notfound.js">
/* this should not be here **/ 
</script>""",
"""XXX""")


    def XXXtestScriptSrc5 (self):
        self.filt(
"""<script src="file:///C:/Progra~1/1.js"></script>

</html>""",
"""XXX""")


    def testCommentQuoting (self):
        self.filt(
"""<script language="JavaScript">
function a () {
}
</script>""",
"""<script language="JavaScript">
<!--
function a () {
}
//-->
</script>""")


    def testFlash (self):
        self.filt(
"""<script language="JavaScript1.1">
<!--
var words = navigator.plugins["Shockwave Flash"].description.split(" ");
//-->
</script>""",
"""<script language="JavaScript1.1">
<!--
var words = navigator.plugins["Shockwave Flash"].description.split(" ");
//-->
</script>""")


    def testHostname (self):
        self.filt(
"""<script language="JavaScript1.1">
<!--
var v1 = document.location.hostname;
var v2 = location.hostname;
//-->
</script>""",
"""<script language="JavaScript1.1">
<!--
var v1 = document.location.hostname;
var v2 = location.hostname;
//-->
</script>""")


    def testNonScript (self):
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


    def testCommentQuoting2 (self):
        self.filt(
"""<script>
<!-- hui
a = 0
// bui -->
</script>""",
"""<script>
<!--
a = 0
//-->
</script>""")


if __name__ == '__main__':
    unittest.main()
