from wc.parser.htmllib import HtmlPrinter
htmldata = """
<html><head>
<!-- closing > before end of tag -->
<!-- <META NAME="Author" CONTENT="Andrew McDonald <andrew@mcdonald.org.uk>"> -->
     <META NAME="Author" CONTENT="Andrew McDonald &lt;andrew@mcdonald.org.uk&gt;">
     
<!-- meta refresh tag -->
<!-- <meta http-equiv="refresh"> -->
     <meta http-equiv="refresh">

<!-- meta ReFresh tag -->
<!-- <meta http-equiv="ReFresh"> -->
     <meta http-equiv="ReFresh">

<!-- meta refrish tag -->
<!-- <meta http-equiv="Refrish"> -->
     <meta http-equiv="Refrish">

<!-- IE shortcut icon and </link> end tag -->
<!-- <link rel="shortcut icon"></link> -->
     <link rel="shortcut icon"></link>
<!-- missing start tag -->
</title>
</head>

<!-- javascript in body tag -->
<!-- <body onload="hulla();" onunload="holla();"> -->
     <body onload="hulla();" onunload="holla();">

<!-- advert links -->
<!-- <a href="http://www.doubleclick.net/">image data and such...</a> -->
     <a href="http://www.doubleclick.net/">image data and such...</a>
<!-- <a href="http://ads.freshmeat.net/">...</a> -->
     <a href="http://ads.freshmeat.net/">...</a>

<!-- replace blink with bold -->
<!-- <blink>blinking text</blink> -->
     <blink>blinking text</blink>

<!-- remove noscript tag -->
<!-- <noscript>Kein Javascript</noscript> -->
     <noscript>Kein Javascript</noscript>

<!-- transform erotic link :) -->
<!-- <a href="http://playboy.com/issue/">blubba</a> -->
     <a href="http://playboy.com/issue/">blubba</a>

<!-- redirect -->
<!-- <a href="http://www.fileleech.com/dl/?filepath=http://www.counter-strike.de/downloads/ghl10full.exe&download=1">CS 1.0</a> -->
     <a href="http://www.fileleech.com/dl/?filepath=http://www.counter-strike.de/downloads/ghl10full.exe&download=1">CS 1.0</a>

<!-- unquoted ampersand -->
<!-- Hallo Ernie & Bert, was geht? -->
     Hallo Ernie & Bert, was geht?

<!-- entityrefs, should be left as is -->
<!-- Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;? -->
     Hallo Ernie &amp; Bert, was geht &lt;ab&gt;&#183;?

<!-- 1x1 image -->
<!-- <img src="blubb" width="1" height="1"> -->
     <img src="blubb" width="1" height="1">

<!-- adlog.pl (freshmeat) -->
<!-- <a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'></a> -->
<a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'></a>

<!-- unquoted attribute ending with slash -->
<!-- <a href=http://www/>link</a> -->
<a href=http://www/>link</a>

<!-- illegal binary chars (see source) -->
These �Microsoft chars� are history.
�Retter� Majak trifft in der Schlussminute. 

<!-- bad quote in tag attributes -->
<!-- <a href="bla" %]">seen at slashdot</a> -->
<a href="bla" %]">seen at slashdot</a>

<!-- no beginning quote -->
<!-- <a href=bla">link</a> -->
<a href=bla">link</a>

<!-- no ending quote -->
<!-- <a href="bla>link</a> -->
<a href=bla">link</a>

<script type="text/javascript" defer>
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
    message = "Calvin w�nscht angenehmes Surfen am " + get_date() + " um " + get_time () + ".";
    w.defaultStatus = message;
}
// end of script. -->
</script>

</body></html>
"""

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
    # more start tags
    """<a b=c"><a b="c">""",
    """<a b="c><a b="c">""",
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
    # start and end tag
    """<a/>""",
    # declaration tags
    """<!DOCTYPE adrbook SYSTEM "adrbook.dtd">""",
    # misc
    """<?xml version="1.0" encoding="latin1"?>""",
    # javascript
    """<script >\n</script>""",
    """<sCrIpt lang="a">bla </a> fasel</scripT>""",
    # line continuation (Dr. Fun webpage)
    "<img bo\\\nrder=0 >",
)

flushtests = (
    "<",
    "<a",
    "<!a",
    "<?a",
)

def _test():
    print "============ syntax tests ============="
    p = HtmlPrinter()
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
    p1 = HtmlPrinter()
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
    p.feed(htmldata)
    p.flush()
    print "finished"

_test()
