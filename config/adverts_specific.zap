<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.429" oid="1" title="Specific adverts"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite sid="wc.398" oid="0" title="Deja.com adverts"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.399" oid="1" title="Heise advert tag"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert"/>


<rewrite sid="wc.400" oid="2" title="Heise advert tag 2"
 desc="heise.de"
 tag="contentbanner"/>


<rewrite sid="wc.401" oid="3" title="Userfriendly outbound links"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.402" oid="4" title="adbouncer"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.403" oid="5" title="easy-cash"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.404" oid="6" title="Salon.com"
 desc="Jump ads at Salon"
 matchurl="salon.com">
<attr>jump.salon.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.405" oid="7" title="OSDN navbar"
 desc="Navigation bar form"
 tag="form">
<attr name="action">http://www\.osdn\.com/osdnsearch\.pl</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.406" oid="8" title="SF tracker image"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.407" oid="9" title="IMDB Advert"
 desc="adverts are redirections"
 matchurl="imdb">
<attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.408" oid="10" title="IMDB Advert 2"
 desc="image map adverts"
 matchurl="imdb"
 tag="area">
<attr>/tiger_redirect\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.409" oid="11" title="IMDB Advert 3"
 desc="The ultimate solution"
 matchurl="imdb"
 tag="img">
<attr name="usemap">^#m_pro-</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.410" oid="12" title="IMDB Advert 4"
 desc="/r/ stuff and imdb pro"
 matchurl="imdb">
<attr>(/r/|/register/subscribe)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.411" oid="13" title="IMDB Advert 5"
 desc="Remove ad pics"
 matchurl="imdb"
 tag="img">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.412" oid="14" title="IMDB Advert 6"
 desc="image tag"
 matchurl="imdb"
 tag="image">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.413" oid="15" title="IMDB Advert 7"
 tag="embed">
<attr name="src">i.imdb.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.414" oid="16" title="Onmouseover ads"
 desc="This gets rid of the latest generation of JavaScript annoyances. ">
<attr name="onmouseover">parent\.location\s*=</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.415" oid="17" title="EOnline ads">
<attr>/cgi-bin/acc_clickthru\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.416" oid="18" title="slashdot ad"
 desc="JS ad at slashdot"
 tag="script">
<attr name="src">s0b\.bluestreak\.com</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.417" oid="19" title="Slashdot JS ad 1"
 scheme="http"
 host="images2.slashdot.org"
 port=""
 path="/Slashdot/pc.gif"
 parameters=""
 query=""
 fragment=""/>

<block sid="wc.418" oid="20" title="Slashdot JS ad 2"
 scheme="http"
 host="images.slashdot.org"
 port=""
 path="/banner/"
 parameters=""
 query=""
 fragment=""/>

<rewrite sid="wc.419" oid="21" title="Atwola JS ad"
 desc="found at fortune.com"
 tag="script">
<attr name="src">ar\.atwola\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.420" oid="22" title="JS .au ad"
 desc="Fairfax advert"
 tag="script">
<attr name="src">http://campaigns\.f2\.com\.au</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.421" oid="23" title="Google Pageads"
 desc="Google Javascript (textual) pageads."
 tag="script">
<attr name="src">pagead\.googlesyndication\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.422" oid="24" title="LWN ad"
 desc="Pagead at linux weekly news"
 matchurl="lwn\.net">
<attr>oasis\.lwn\.net/oasisc\.php</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.423" oid="25" title="Freshmeat ads"
 desc="Freshmeat ad server"
 matchurl="freshmeat.net"
 tag="img">
<attr name="src">fmads.osdn.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.424" oid="26" title="maxihitz"
 tag="iframe">
<attr name="src">maxihitz\.de</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.425" oid="27" title="Schmidtie"
 desc="Harald-Schmidt-Show homepage sux"
 matchurl="www.sat1.de">
<attr>/jump\.hbs</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.426" oid="28" title="MSN ads"
 desc="Found at MSN">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.427" oid="29" title="MSN ads 2"
 desc="Same as MSN ads, only in area"
 tag="area">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.428" oid="30" title="Falk ag link">
<attr>as1\.falkag\.de/server/link\.asp</attr>
<replacement part="complete"/>
</rewrite>
</folder>
