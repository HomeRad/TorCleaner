<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.429" oid="4">
<title lang="de">Spezielle Werbung</title>
<title lang="en">Specific adverts</title>
<description lang="en">A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.</description>

<rewrite sid="wc.398">
  <title lang="en">Deja.com adverts</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>www\.deja\.com/jump/</attr>
</rewrite>

<rewrite sid="wc.399"
 tag="heiseadvert">
  <title lang="en">Heise advert</title>
  <description lang="en">www.heise.de has an advert tag. Nice :)</description>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>

<rewrite sid="wc.400"
 tag="contentbanner">
  <title lang="en">Heise contentbanner</title>
  <description lang="en">heise.de</description>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>

<rewrite sid="wc.12"
 tag="skyscraper">
  <title lang="en">Heise skyscraper</title>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>

<rewrite sid="wc.11"
 tag="table">
  <title lang="en">Heise Onlinemarkt</title>
  <attr name="cellpadding">^2$</attr>
  <attr name="bgcolor">^#EEEEEE$</attr>
  <attr name="width">^137$</attr>
  <enclosed>&lt;big&gt;O&lt;/big&gt;NLINE-&lt;big&gt;M&lt;/big&gt;</enclosed>
</rewrite>

<rewrite sid="wc.401">
  <title lang="en">Userfriendly outbound links</title>
  <description lang="en">Links on userfriendly.org which point outbound. This is a redirector host.</description>
  <attr>https?://links\.userfriendly\.org</attr>
</rewrite>

<rewrite sid="wc.402">
  <title lang="en">adbouncer</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/adbouncer\.phtml</attr>
</rewrite>

<rewrite sid="wc.403">
  <title lang="en">easy-cash</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>easy-cash</attr>
</rewrite>

<rewrite sid="wc.404">
  <title lang="en">Salon.com</title>
  <description lang="en">Jump ads at Salon</description>
  <matchurl>salon\.com</matchurl>
  <attr>jump.salon.com</attr>
</rewrite>

<rewrite sid="wc.405"
 tag="table">
  <title lang="en">Freshmeat OSDN navbar</title>
  <description lang="en">I don&apos;t like the OSDN navigation bar.</description>
  <matchurl>^http://freshmeat\.net/</matchurl>
  <attr name="style">border-top: 1px #6f6f6f solid; border-bottom: 1px #6f6f6f solid;</attr>
</rewrite>

<rewrite sid="wc.9"
 tag="table">
  <title lang="en">Slashdot OSDN navbar</title>
  <description lang="en">I don&apos;t like the OSDN navbar.</description>
  <matchurl>^http://slashdot\.org/</matchurl>
  <attr name="style">border-top: 1px #999999 solid; border-bottom: 5px #000000 solid</attr>
</rewrite>

<rewrite sid="wc.10"
 tag="table">
  <title lang="en">Sourceforge ODSN navbar</title>
  <description lang="en">Sourceforge ODSN navbar</description>
  <matchurl>^http://(sf|sourceforge)\.net/</matchurl>
  <attr name="style">border-top: 2px #666666 solid; border-bottom:\s*1px #222222 solid;</attr>
</rewrite>

<rewrite sid="wc.406"
 tag="img">
  <title lang="en">SF tracker image</title>
  <description lang="en">akamai tracker image at sourceforge</description>
  <attr name="src">e\.akamai\.net</attr>
</rewrite>

<rewrite sid="wc.407">
  <title lang="en">IMDB Advert</title>
  <description lang="en">adverts are redirections</description>
  <matchurl>imdb\.</matchurl>
  <attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
</rewrite>

<rewrite sid="wc.408"
 tag="area">
  <title lang="en">IMDB Advert 2</title>
  <description lang="en">image map adverts</description>
  <matchurl>imdb\.</matchurl>
  <attr>/tiger_redirect\?</attr>
</rewrite>

<rewrite sid="wc.409"
 tag="img">
  <title lang="en">IMDB Advert 3</title>
  <description lang="en">The ultimate solution</description>
  <matchurl>imdb\.</matchurl>
  <attr name="usemap">^#m_pro-</attr>
</rewrite>

<rewrite sid="wc.410">
  <title lang="en">IMDB Advert 4</title>
  <description lang="en">/r/ stuff and imdb pro</description>
  <matchurl>imdb\.</matchurl>
  <attr>(/r/|/register/subscribe)</attr>
</rewrite>

<rewrite sid="wc.411"
 tag="img">
  <title lang="en">IMDB Advert 5</title>
  <description lang="en">Remove ad pictures</description>
  <matchurl>imdb\.</matchurl>
  <attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</rewrite>

<rewrite sid="wc.412"
 tag="image">
  <title lang="en">IMDB Advert 6</title>
  <description lang="en">image tag</description>
  <matchurl>imdb\.</matchurl>
  <attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</rewrite>

<rewrite sid="wc.413"
 tag="embed">
  <title lang="en">IMDB Advert 7</title>
  <attr name="src">ia?\.imdb\.com</attr>
</rewrite>

<rewrite sid="wc.414">
  <title lang="en">Onmouseover ads</title>
  <description lang="en">This gets rid of the latest generation of JavaScript annoyances.</description>
  <attr name="onmouseover">parent\.location\s*=</attr>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.415">
  <title lang="en">EOnline ads</title>
  <attr>/cgi-bin/acc_clickthru\?</attr>
</rewrite>

<rewrite sid="wc.416"
 tag="script">
  <title lang="en">slashdot ad</title>
  <description lang="en">JS ad at slashdot</description>
  <attr name="src">s0b\.bluestreak\.com</attr>
</rewrite>

<block sid="wc.417"
 url="https?://images2.slashdot.org/Slashdot/pc.gif">
  <title lang="en">Slashdot JS ad 1</title>
</block>

<block sid="wc.418"
 url="https?://images.slashdot.org/banner/">
  <title lang="en">Slashdot JS ad 2</title>
</block>

<rewrite sid="wc.419"
 tag="script">
  <title lang="en">Atwola JS ad</title>
  <description lang="en">found at fortune.com</description>
  <attr name="src">ar\.atwola\.com</attr>
</rewrite>

<rewrite sid="wc.420"
 tag="script">
  <title lang="en">JS .au ad</title>
  <description lang="en">Fairfax advert</description>
  <attr name="src">http://campaigns\.f2\.com\.au</attr>
</rewrite>

<rewrite sid="wc.421"
 tag="script">
  <title lang="en">Google Pageads</title>
  <description lang="en">Google Javascript (textual) pageads.</description>
  <attr name="src">pagead\.googlesyndication\.com</attr>
</rewrite>

<rewrite sid="wc.422">
  <title lang="en">LWN ad</title>
  <description lang="en">Pagead at linux weekly news</description>
  <matchurl>lwn\.net</matchurl>
  <attr>oasis\.lwn\.net/oasisc\.php</attr>
</rewrite>

<rewrite sid="wc.423"
 tag="img">
  <title lang="en">Freshmeat ads</title>
  <description lang="en">Freshmeat ad server</description>
  <matchurl>freshmeat\.net</matchurl>
  <attr name="src">fmads\.osdn\.com</attr>
</rewrite>

<rewrite sid="wc.425">
  <title lang="en">Schmidtie</title>
  <description lang="en">Harald-Schmidt-Show homepage sux</description>
  <matchurl>www\.sat1\.de</matchurl>
  <attr>/jump\.hbs</attr>
</rewrite>

<rewrite sid="wc.424"
 tag="iframe">
  <title lang="en">maxihitz</title>
  <attr name="src">maxihitz\.de</attr>
</rewrite>

<rewrite sid="wc.426">
  <title lang="en">MSN ads</title>
  <description lang="en">Found at MSN</description>
  <attr>g\.msn(bc)?\.com</attr>
</rewrite>

<rewrite sid="wc.427"
 tag="area">
  <title lang="en">MSN ads 2</title>
  <description lang="en">Same as MSN ads, only in area</description>
  <attr>g\.msn(bc)?\.com</attr>
</rewrite>

<rewrite sid="wc.428">
  <title lang="en">Falk ag link</title>
  <attr>as1\.falkag\.de/server/link\.asp</attr>
</rewrite>
</folder>
