<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.429" title="Specific adverts"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it." oid="1">
<rewrite sid="wc.398" title="Deja.com adverts"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.399" title="Heise advert"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert">
<matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>


<rewrite sid="wc.400" title="Heise contentbanner"
 desc="heise.de"
 tag="contentbanner">
<matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>


<rewrite sid="wc.12" title="Heise skyscraper"
 tag="skyscraper">
<matchurl>^http://(www\.)heise\.de/</matchurl>
</rewrite>


<rewrite sid="wc.11" title="Heise Onlinemarkt"
 tag="table">
<attr name="cellpadding">^2$</attr>
<attr name="bgcolor">^#EEEEEE$</attr>
<attr name="width">^137$</attr>
<enclosed>&lt;big&gt;O&lt;/big&gt;NLINE-&lt;big&gt;M&lt;/big&gt;</enclosed>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.401" title="Userfriendly outbound links"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>https?://links\.userfriendly\.org</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.402" title="adbouncer"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.403" title="easy-cash"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.404" title="Salon.com"
 desc="Jump ads at Salon">
<matchurl>salon\.com</matchurl>
<attr>jump.salon.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.405" title="Freshmeat OSDN navbar"
 desc="I don&apos;t like the OSDN navigation bar."
 tag="table">
<matchurl>^http://freshmeat\.net/</matchurl>
<attr name="style">border-top: 1px #6f6f6f solid; border-bottom: 1px #6f6f6f solid;</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.9" title="Slashdot OSDN navbar"
 desc="I don&apos;t like the OSDN navbar."
 tag="table">
<matchurl>^http://slashdot\.org/</matchurl>
<attr name="style">border-top: 1px #999999 solid; border-bottom: 5px #000000 solid</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.10" title="Sourceforge ODSN navbar"
 desc="I don&apos;t like the navbar"
 tag="table">
<matchurl>^http://(sf|sourceforge)\.net/</matchurl>
<attr name="style">border-top: 2px #666666 solid; border-bottom:\s*1px #222222 solid;</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.406" title="SF tracker image"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.407" title="IMDB Advert"
 desc="adverts are redirections">
<matchurl>imdb\.</matchurl>
<attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.408" title="IMDB Advert 2"
 desc="image map adverts"
 tag="area">
<matchurl>imdb\.</matchurl>
<attr>/tiger_redirect\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.409" title="IMDB Advert 3"
 desc="The ultimate solution"
 tag="img">
<matchurl>imdb\.</matchurl>
<attr name="usemap">^#m_pro-</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.410" title="IMDB Advert 4"
 desc="/r/ stuff and imdb pro">
<matchurl>imdb\.</matchurl>
<attr>(/r/|/register/subscribe)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.411" title="IMDB Advert 5"
 desc="Remove ad pictures"
 tag="img">
<matchurl>imdb\.</matchurl>
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.412" title="IMDB Advert 6"
 desc="image tag"
 tag="image">
<matchurl>imdb\.</matchurl>
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.413" title="IMDB Advert 7"
 tag="embed">
<attr name="src">ia?\.imdb\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.414" title="Onmouseover ads"
 desc="This gets rid of the latest generation of JavaScript annoyances. ">
<attr name="onmouseover">parent\.location\s*=</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.415" title="EOnline ads">
<attr>/cgi-bin/acc_clickthru\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.416" title="slashdot ad"
 desc="JS ad at slashdot"
 tag="script">
<attr name="src">s0b\.bluestreak\.com</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.417" title="Slashdot JS ad 1"
 url="https?://images2.slashdot.org/Slashdot/pc.gif"/>

<block sid="wc.418" title="Slashdot JS ad 2"
 url="https?://images.slashdot.org/banner/"/>

<rewrite sid="wc.419" title="Atwola JS ad"
 desc="found at fortune.com"
 tag="script">
<attr name="src">ar\.atwola\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.420" title="JS .au ad"
 desc="Fairfax advert"
 tag="script">
<attr name="src">http://campaigns\.f2\.com\.au</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.421" title="Google Pageads"
 desc="Google Javascript (textual) pageads."
 tag="script">
<attr name="src">pagead\.googlesyndication\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.422" title="LWN ad"
 desc="Pagead at linux weekly news">
<matchurl>lwn\.net</matchurl>
<attr>oasis\.lwn\.net/oasisc\.php</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.423" title="Freshmeat ads"
 desc="Freshmeat ad server"
 tag="img">
<matchurl>freshmeat\.net</matchurl>
<attr name="src">fmads\.osdn\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.424" title="maxihitz"
 tag="iframe">
<attr name="src">maxihitz\.de</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.425" title="Schmidtie"
 desc="Harald-Schmidt-Show homepage sux">
<matchurl>www\.sat1\.de</matchurl>
<attr>/jump\.hbs</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.426" title="MSN ads"
 desc="Found at MSN">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.427" title="MSN ads 2"
 desc="Same as MSN ads, only in area"
 tag="area">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.428" title="Falk ag link">
<attr>as1\.falkag\.de/server/link\.asp</attr>
<replacement part="complete"/>
</rewrite>
</folder>
