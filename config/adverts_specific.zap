<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Adverts" oid="0"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="Deja.com adverts" oid="26"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Heise advert tag" oid="27"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert"/>


<rewrite title="Heise advert tag 2" oid="28"
 desc="heise.de"
 tag="contentbanner"/>


<rewrite title="Userfriendly outbound links" oid="29"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="adbouncer" oid="30"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="easy-cash" oid="31"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Salon.com" oid="32"
 desc="Jump ads at Salon"
 matchurl="salon.com">
<attr>jump.salon.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="OSDN navbar" oid="33"
 desc="Navigation bar form"
 tag="form">
<attr name="action">http://www\.osdn\.com/osdnsearch\.pl</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="SF tracker image" oid="34"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert" oid="35"
 desc="adverts are redirections"
 matchurl="imdb">
<attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 2" oid="36"
 desc="image map adverts"
 matchurl="imdb"
 tag="area">
<attr>/tiger_redirect\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 3" oid="37"
 desc="The ultimate solution"
 matchurl="imdb"
 tag="img">
<attr name="usemap">^#m_pro-</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 4" oid="38"
 desc="/r/ stuff and imdb pro"
 matchurl="imdb">
<attr>(/r/|/register/subscribe)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 5" oid="39"
 desc="Remove ad pics"
 matchurl="imdb"
 tag="img">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 6" oid="40"
 desc="image tag"
 matchurl="imdb"
 tag="image">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 7" oid="41"
 tag="embed">
<attr name="src">i.imdb.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Onmouseover ads" oid="42"
 desc="This gets rid of the latest generation of JavaScript annoyances. ">
<attr name="onmouseover">parent\.location\s*=</attr>
<replacement part="attr"/>
</rewrite>

<rewrite title="EOnline ads" oid="43">
<attr>/cgi-bin/acc_clickthru\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="slashdot ad" oid="44"
 desc="JS ad at slashdot"
 tag="script">
<attr name="src">s0b\.bluestreak\.com</attr>
<replacement part="complete"/>
</rewrite>

<block title="Slashdot JS ad 1" oid="45"
 scheme="http"
 host="images2.slashdot.org"
 port=""
 path="/Slashdot/pc.gif"
 parameters=""
 query=""
 fragment=""/>

<block title="Slashdot JS ad 2" oid="46"
 scheme="http"
 host="images.slashdot.org"
 port=""
 path="/banner/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Atwola JS ad" oid="47"
 desc="found at fortune.com"
 tag="script">
<attr name="src">ar\.atwola\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="JS .au ad" oid="48"
 desc="Fairfax advert"
 tag="script">
<attr name="src">http://campaigns\.f2\.com\.au</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Google Pageads" oid="49"
 desc="Google Javascript (textual) pageads."
 tag="script">
<attr name="src">pagead\.googlesyndication\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="LWN ad" oid="50"
 desc="Pagead at linux weekly news"
 matchurl="lwn\.net">
<attr>oasis\.lwn\.net/oasisc\.php</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Freshmeat ads" oid="51"
 desc="Freshmeat ad server"
 matchurl="freshmeat.net"
 tag="img">
<attr name="src">fmads.osdn.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="maxihitz" oid="52"
 tag="iframe">
<attr name="src">maxihitz\.de</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Schmidtie" oid="53"
 desc="Harald-Schmidt-Show homepage sux"
 matchurl="www.sat1.de">
<attr>/jump\.hbs</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="MSN ads" oid="54"
 desc="Found at MSN">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="MSN ads 2" oid="55"
 desc="Same as MSN ads, only in area"
 tag="area">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Falk ag link" oid="56">
<attr>as1\.falkag\.de/server/link\.asp</attr>
<replacement part="complete"/>
</rewrite>
</folder>
