<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Specific adverts" oid="1"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="Deja.com adverts" oid="0"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Heise advert tag" oid="1"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert"/>


<rewrite title="Heise advert tag 2" oid="2"
 desc="heise.de"
 tag="contentbanner"/>


<rewrite title="Userfriendly outbound links" oid="3"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="adbouncer" oid="4"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="easy-cash" oid="5"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Salon.com" oid="6"
 desc="Jump ads at Salon"
 matchurl="salon.com">
<attr>jump.salon.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="OSDN navbar" oid="7"
 desc="Navigation bar form"
 tag="form">
<attr name="action">http://www\.osdn\.com/osdnsearch\.pl</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="SF tracker image" oid="8"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert" oid="9"
 desc="adverts are redirections"
 matchurl="imdb">
<attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS|TSEARCH|TSEARCH_RHS|[A-Z_]*AD_LOWRES|[A-Z_]*LOWRES_BUY|EGAL_[A-Z]+)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 2" oid="10"
 desc="image map adverts"
 matchurl="imdb"
 tag="area">
<attr>/tiger_redirect\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 3" oid="11"
 desc="The ultimate solution"
 matchurl="imdb"
 tag="img">
<attr name="usemap">^#m_pro-</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 4" oid="12"
 desc="/r/ stuff and imdb pro"
 matchurl="imdb">
<attr>(/r/|/register/subscribe)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 5" oid="13"
 desc="Remove ad pics"
 matchurl="imdb"
 tag="img">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 6" oid="14"
 desc="image tag"
 matchurl="imdb"
 tag="image">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="IMDB Advert 7" oid="15"
 tag="embed">
<attr name="src">i.imdb.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Onmouseover ads" oid="16"
 desc="This gets rid of the latest generation of JavaScript annoyances. ">
<attr name="onmouseover">parent\.location\s*=</attr>
<replacement part="attr"/>
</rewrite>

<rewrite title="EOnline ads" oid="17">
<attr>/cgi-bin/acc_clickthru\?</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="slashdot ad" oid="18"
 desc="JS ad at slashdot"
 tag="script">
<attr name="src">s0b\.bluestreak\.com</attr>
<replacement part="complete"/>
</rewrite>

<block title="Slashdot JS ad 1" oid="19"
 scheme="http"
 host="images2.slashdot.org"
 port=""
 path="/Slashdot/pc.gif"
 parameters=""
 query=""
 fragment=""/>

<block title="Slashdot JS ad 2" oid="20"
 scheme="http"
 host="images.slashdot.org"
 port=""
 path="/banner/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Atwola JS ad" oid="21"
 desc="found at fortune.com"
 tag="script">
<attr name="src">ar\.atwola\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="JS .au ad" oid="22"
 desc="Fairfax advert"
 tag="script">
<attr name="src">http://campaigns\.f2\.com\.au</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Google Pageads" oid="23"
 desc="Google Javascript (textual) pageads."
 tag="script">
<attr name="src">pagead\.googlesyndication\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="LWN ad" oid="24"
 desc="Pagead at linux weekly news"
 matchurl="lwn\.net">
<attr>oasis\.lwn\.net/oasisc\.php</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Freshmeat ads" oid="25"
 desc="Freshmeat ad server"
 matchurl="freshmeat.net"
 tag="img">
<attr name="src">fmads.osdn.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="maxihitz" oid="26"
 tag="iframe">
<attr name="src">maxihitz\.de</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Schmidtie" oid="27"
 desc="Harald-Schmidt-Show homepage sux"
 matchurl="www.sat1.de">
<attr>/jump\.hbs</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="MSN ads" oid="28"
 desc="Found at MSN">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="MSN ads 2" oid="29"
 desc="Same as MSN ads, only in area"
 tag="area">
<attr>g\.msn(bc)?\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Falk ag link" oid="30">
<attr>as1\.falkag\.de/server/link\.asp</attr>
<replacement part="complete"/>
</rewrite>
</folder>
