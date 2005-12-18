<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.429" oid="4" configversion="0.10">
<title lang="de">Spezielle Werbung</title>
<title lang="en">Specific adverts</title>
<description lang="en">A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href="http://company.com"&gt;&lt;img  src="http://adserver.de/banner.gif"&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.</description>

<htmlrewrite sid="wc.398"
 tag="a">
  <title lang="de">www.deja.com</title>
  <title lang="en">Deja.com adverts</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr name="href">www\.deja\.com/jump/</attr>
</htmlrewrite>

<htmlrewrite sid="wc.399"
 tag="heiseadvert">
  <title lang="de">heise.de &lt;heiseadvert&gt;</title>
  <title lang="en">Heise advert</title>
  <description lang="de">Heise besitzt ein advert tag :)</description>
  <description lang="en">www.heise.de has an advert tag. Nice :)</description>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</htmlrewrite>

<htmlrewrite sid="wc.400"
 tag="contentbanner">
  <title lang="de">heise.de &lt;contentbanner&gt;</title>
  <title lang="en">Heise contentbanner</title>
  <description lang="en">heise.de</description>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</htmlrewrite>

<htmlrewrite sid="wc.12"
 tag="skyscraper">
  <title lang="de">heise.de &lt;skyscraper&gt;</title>
  <title lang="en">Heise skyscraper</title>
  <matchurl>^http://(www\.)heise\.de/</matchurl>
</htmlrewrite>

<htmlrewrite sid="wc.11"
 tag="table">
  <title lang="de">heise.de Onlinemarkt</title>
  <title lang="en">Heise Onlinemarkt</title>
  <matchurl>(www\.)?heise\.de</matchurl>
  <attr name="cellpadding">^2$</attr>
  <attr name="bgcolor">^#EEEEEE$</attr>
  <attr name="width">^137$</attr>
  <enclosed>&lt;big&gt;O&lt;/big&gt;NLINE-&lt;big&gt;M&lt;/big&gt;</enclosed>
</htmlrewrite>

<htmlrewrite sid="wc.401"
 tag="a">
  <title lang="de">userfriendly.org</title>
  <title lang="en">Userfriendly outbound links</title>
  <description lang="en">Links on userfriendly.org which point outbound. This is a redirector host.</description>
  <attr name="href">https?://links\.userfriendly\.org</attr>
</htmlrewrite>

<htmlrewrite sid="wc.404"
 tag="a">
  <title lang="de">salon.com</title>
  <title lang="en">Salon.com</title>
  <description lang="de">jump.salon.com Verknüpfungen sind Werbung.</description>
  <description lang="en">Jump ads at Salon</description>
  <matchurl>salon\.com</matchurl>
  <attr name="href">jump.salon.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.405"
 tag="table">
  <title lang="de">freshmeat.net</title>
  <title lang="en">Freshmeat OSDN navbar</title>
  <description lang="de">Ich mag die OSDN Leiste nicht.</description>
  <description lang="en">I don't like the OSDN navigation bar.</description>
  <matchurl>^http://freshmeat\.net/</matchurl>
  <attr name="style">border-top: 1px #6f6f6f solid; border-bottom: 1px #6f6f6f solid;</attr>
</htmlrewrite>

<htmlrewrite sid="wc.9"
 tag="ul">
  <title lang="de">slashdot.org</title>
  <title lang="en">Slashdot OSDN navbar</title>
  <description lang="de">Ich mag die OSDN Leiste nicht.</description>
  <description lang="en">I don't like the OSDN navbar.</description>
  <matchurl>^http://slashdot\.org/</matchurl>
  <attr name="id">ostgnavbar</attr>
</htmlrewrite>

<htmlrewrite sid="wc.10"
 tag="ul">
  <title lang="de">sourceforge.net</title>
  <title lang="en">Sourceforge ODSN navbar</title>
  <description lang="de">Ich mag die OSDN Leiste nicht.</description>
  <description lang="en">Sourceforge ODSN navbar</description>
  <matchurl>^http://(sf|sourceforge)\.net/</matchurl>
  <attr name="class">ostgnavbar</attr>
</htmlrewrite>

<htmlrewrite sid="wc.407"
 tag="a">
  <title lang="de">IMDB Werbung 1</title>
  <title lang="en">IMDB Advert</title>
  <description lang="de">tiger_redirect Werbung</description>
  <description lang="en">adverts are redirections</description>
  <matchurl>imdb\.</matchurl>
  <attr name="href">/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.408"
 tag="area">
  <title lang="de">IMDB Werbung 2</title>
  <title lang="en">IMDB Advert 2</title>
  <description lang="de">Werbung in Image Maps.</description>
  <description lang="en">image map adverts</description>
  <matchurl>imdb\.</matchurl>
  <attr name="href">/tiger_redirect\?</attr>
</htmlrewrite>

<htmlrewrite sid="wc.409"
 tag="img">
  <title lang="de">IMDB Werbung 3</title>
  <title lang="en">IMDB Advert 3</title>
  <description lang="de">Die ultimative Lösung</description>
  <description lang="en">The ultimate solution</description>
  <matchurl>imdb\.</matchurl>
  <attr name="usemap">^#m_pro-</attr>
</htmlrewrite>

<htmlrewrite sid="wc.410"
 tag="a">
  <title lang="de">IMDB Werbung 4</title>
  <title lang="en">IMDB Advert 4</title>
  <description lang="de">/r/ Zeugs und IMDB Pro</description>
  <description lang="en">/r/ stuff and imdb pro</description>
  <matchurl>imdb\.</matchurl>
  <attr name="href">(/r/|/register/subscribe)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.411"
 tag="img">
  <title lang="de">IMDB Werbung 5</title>
  <title lang="en">IMDB Advert 5</title>
  <description lang="de">Entferne Werbebilder</description>
  <description lang="en">Remove ad pictures</description>
  <matchurl>imdb\.</matchurl>
  <attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.412"
 tag="image">
  <title lang="de">IMDB Werbung 6</title>
  <title lang="en">IMDB Advert 6</title>
  <description lang="de">Noch mehr Werbebilder</description>
  <description lang="en">image tag</description>
  <matchurl>imdb\.</matchurl>
  <attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.413"
 tag="embed">
  <title lang="de">IMDB Werbung 7</title>
  <title lang="en">IMDB Advert 7</title>
  <attr name="src">ia?\.imdb\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.415"
 tag="a">
  <title lang="de">EOnline Werbung</title>
  <title lang="en">EOnline ads</title>
  <attr name="href">/cgi-bin/acc_clickthru\?</attr>
</htmlrewrite>

<htmlrewrite sid="wc.416"
 tag="script">
  <title lang="de">slashdot Werbung</title>
  <title lang="en">slashdot ad</title>
  <description lang="en">JS ad at slashdot</description>
  <attr name="src">s0b\.bluestreak\.com</attr>
</htmlrewrite>

<block sid="wc.417"
 url="https?://images2.slashdot.org/Slashdot/pc.gif">
  <title lang="de">slashdot.org Bilder 1</title>
  <title lang="en">Slashdot JS ad 1</title>
</block>

<block sid="wc.418"
 url="https?://images.slashdot.org/banner/">
  <title lang="de">slashdot.org Bilder 2</title>
  <title lang="en">Slashdot JS ad 2</title>
</block>

<htmlrewrite sid="wc.419"
 tag="script">
  <title lang="de">atwola.com Werbung</title>
  <title lang="en">Atwola JS ad</title>
  <description lang="en">found at fortune.com</description>
  <attr name="src">ar\.atwola\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.420"
 tag="script">
  <title lang="de">Fairfax Werbung</title>
  <title lang="en">JS .au ad</title>
  <description lang="en">Fairfax advert</description>
  <attr name="src">http://campaigns\.f2\.com\.au</attr>
</htmlrewrite>

<htmlrewrite sid="wc.421"
 tag="script">
  <title lang="de">Google Werbeseiten</title>
  <title lang="en">Google Pageads</title>
  <description lang="de">Google Javascript (Text-)Werbung.</description>
  <description lang="en">Google Javascript (textual) pageads.</description>
  <attr name="src">pagead\.googlesyndication\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.422"
 tag="a">
  <title lang="de">lwn.net Werbung</title>
  <title lang="en">LWN ad</title>
  <description lang="en">Pagead at linux weekly news</description>
  <matchurl>lwn\.net</matchurl>
  <attr name="href">oasis\.lwn\.net/oasisc\.php</attr>
</htmlrewrite>

<htmlrewrite sid="wc.423"
 tag="img">
  <title lang="de">OSDN Werbung</title>
  <title lang="en">Freshmeat ads</title>
  <description lang="de">OSDN Werbung bei freshmeat.net und anderen.</description>
  <description lang="en">Freshmeat ad server</description>
  <attr name="src">fmads\.osdn\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.26"
 tag="a">
  <title lang="de">OSDN Werbung 2</title>
  <attr name="href">ads\d\.osdn\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.425"
 tag="a">
  <title lang="en">Schmidtie</title>
  <description lang="de">Harald-Schmidt-Show homepage suxxorz</description>
  <description lang="en">Harald-Schmidt-Show homepage sux</description>
  <matchurl>www\.sat1\.de</matchurl>
  <attr name="href">/jump\.hbs</attr>
</htmlrewrite>

<htmlrewrite sid="wc.426"
 tag="a">
  <title lang="de">MSN Werbungen</title>
  <title lang="en">MSN ads</title>
  <description lang="en">Found at MSN</description>
  <attr name="href">g\.msn(bc)?\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.427"
 tag="area">
  <title lang="de">MSN Werbungen 2</title>
  <title lang="en">MSN ads 2</title>
  <description lang="de">Diesmal im area tag</description>
  <description lang="en">Same as MSN ads, only in area</description>
  <attr name="href">g\.msn(bc)?\.com</attr>
</htmlrewrite>

<htmlrewrite sid="wc.428"
 tag="a">
  <title lang="de">Falk AG Verknüpfungen</title>
  <title lang="en">Falk ag link</title>
  <attr name="href">as1\.falkag\.de/server/link\.asp</attr>
</htmlrewrite>

<htmlrewrite sid="wc.28"
 tag="table">
  <title lang="de">Google Suche Werbungen</title>
  <title lang="en">Google search ads</title>
  <matchurl>www\.google\.</matchurl>
  <attr name="width">^(25|100)%$</attr>
  <enclosed>&amp;ai=A</enclosed>
</htmlrewrite>

<block sid="wc.30"
 url="\.googlesyndication\.">
  <title lang="de">Google pageads</title>
</block>

<htmlrewrite sid="wc.49"
 tag="script">
  <title lang="de">Google annoyances</title>
  <attr name="src">\.google(syndication|-analytics)\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.50"
 tag="iframe">
  <title lang="de">Google pageads 3</title>
  <attr name="src">\.googlesyndication\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.32"
 tag="a">
  <title lang="de">Blog Werbungen</title>
  <title lang="en">Blog ads</title>
  <attr name="href">blogads\.com</attr>
</htmlrewrite>
</folder>
