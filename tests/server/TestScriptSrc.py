# -*- coding: iso-8859-1 -*-
"""test javascript filtering"""

import unittest, os, sys
from test import disable_rating_rules
import wc
from tests import HttpServer
from tests.StandardTest import StandardTest
from wc.proxy import proxy_poll, run_timers
from wc.proxy.Headers import WcMessage
from wc.filter import FilterException
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY


jsfiles = {
    "/1.js": """// check url validity
function isValid (thisForm) {
    if (thisForm.url.value=="" || thisForm.url.value=="http://") {
        alert(gettext("Empty URL was given."));
        thisForm.url.select();
        thisForm.url.focus();
        return false;
    }
    if (!checkSyntax(thisForm.url.value)) {
        alert(gettext("Invalid URL was given."));
        thisForm.url.select();
        thisForm.url.focus();
        return false;
    }
    return true;
}

// check url syntax
function checkSyntax (url) {
    var syntax = /^https?:\/\/[-a-zA-Z.\/=%?~]+$/;
    return syntax.test(url);
}
""",

    "/2.js": """document.write('<iframe frameborder="0" framespacing="0" marginheight="0" marginwidth="0" scrolling="no" src="http://www.n24.de/service/dynabanner/n24_banner.html" vspace="0" width="468" height="60" border="0"></iframe>');
<!--
soi_place=escape("fullbanner2");soi_ad=escape("030219 dynamic banner 468 ohne Clicks (18095)");soi_adplace=soi_place+escape(" - ")+soi_ad+" \n";if (soi_adtrace) soi_adtrace+=soi_adplace;else var soi_adtrace=soi_adplace;soi_ad=soi_ad.toLowerCase();if (window.add2tag){if ((soi_ad.indexOf("powerlayer") > -1) || (soi_ad.indexOf("interstitial") > -1) || (soi_ad.indexOf("popup") > -1)) {add2tag += "&sowefo_ausschluss=powerlayer_popup_interstitial";}}
//-->
""",

    "/3.js": """window.open("datei.htm","Fenster1","width=310,height=400,left=0,top=0");
""",
}

class JSRequestHandler (HttpServer.LogRequestHandler):

    def do_GET (self):
        """serve JavaScript files"""
        self.server.log.write("server got request path %r\n"%self.path)
        if not jsfiles.has_key(self.path):
            data = "HTTP/1.1 404 Oops\r\n"
            body = ""
        else:
            data = 'HTTP/1.1 200 OK\r\n'
            body = jsfiles[self.path]
        data += "Date: %s\r\n" % self.date_time_string()
        data += "Connection: close\r\n"
        data += "Content-Length: %d\r\n" % len(body)
        data += "\r\n"
        data += body
        self.server.log.write("server will send %d bytes\n" % len(data))
        self.print_lines(data)
        self.wfile.write(data)


class TestScriptSrc (StandardTest):
    """All these tests work with a _default_ filter configuration.
       If you change any of the *.zap filter configs, tests can fail..."""

    def init (self):
        super(TestScriptSrc, self).init()
        wc.config = wc.Configuration()
        disable_rating_rules(wc.config)
        wc.config['filters'] = ['Rewriter',]
        wc.config.init_filter_modules()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/html"
        if self.showAll:
            self.log = sys.stdout
        else:
            self.log = file("servertests.txt", 'a')
        self.serverthread = HttpServer.startServer(self.log,
                                       handler_class=JSRequestHandler)

    def shutdown (self):
        """Stop server, close log"""
        HttpServer.stopServer(self.log)
        if not self.showAll:
            self.log.close()

    def filt (self, data, result, name=""):
        attrs = get_filterattrs(name, [FILTER_RESPONSE_MODIFY], headers=self.headers)
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


    def testScriptSrc1 (self):
        self.filt(
"""<script src="http://localhost:%d/1.js"></script>

</html>""" % HttpServer.defaultconfig['port'],
"""<script type="text/javascript">
<!--
%s//-->
</script>

</html>""" % jsfiles['/1.js'])


    def testScriptSrc2 (self):
        self.filt(
"""<script src="http://localhost:%d/1.js">
 
</script>

</html>""" % HttpServer.defaultconfig['port'],
"""<script type="text/javascript">
<!--
%s//-->
</script>

</html>""" % jsfiles['/1.js'])


    def testScriptSrc3 (self):
        """missing </script>"""
        self.filt(
"""<script src="http://localhost:%d/3.js"/>
<script type="JavaScript">
<!--
a = 1
//-->
</script>

</html>""" % HttpServer.defaultconfig['port'],
"""
<script type="JavaScript">
<!--
a = 1
//-->
</script>

</html>""")


    def testRecursionSrc (self):
        self.filt(
"""<script language="JavaScript">
<!--
document.write('<SCR'+'IPT LANGUAGE="JavaScript1.1" ' );
document.write('SRC="http://localhost:%d/2.js">');
document.write('</SCR'+'IPT>');
//-->
</script>
      </td>
   </tr>
</table>""" % HttpServer.defaultconfig['port'],
"""
      </td>
   </tr>
</table>""")


if __name__ == '__main__':
    unittest.main(defaultTest='TestScriptSrc')
else:
    suite = unittest.makeSuite(TestScriptSrc, 'test')
