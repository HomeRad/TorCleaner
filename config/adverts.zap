<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Advertisements" oid="7"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="/werbung" oid="0"
 desc="Kill links with the german ad word in the path.">
<attr>/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
</rewrite>

<rewrite title="Ad servers 01" oid="1"
 desc="Kill links with &apos;ad&apos; in the host name.">
<attr>http://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
</rewrite>

<rewrite title="Ad servers 10" oid="2"
 desc="Kill links with &apos;click&apos; words in the host name.">
<attr>http://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
</rewrite>

<rewrite title="Ad servers 02" oid="3"
 desc="Kill links with ad words in the host name.">
<attr>http://[^/]*(tradedoubler|emerchandise|ecommercetimes)\.</attr>
</rewrite>

<rewrite title="counter and tracker" oid="4"
 desc="Kill tracker and counter cgi scripts.">
<attr>/.*(count|track)(er|run)?\.(pl|cgi|exe|dll|asp|php[34]?)</attr>
</rewrite>

<rewrite title="Ad servers 05" oid="5"
 desc="Kill links with ad words in the host name.">
<attr>http://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
</rewrite>

<rewrite title="Ad servers 06" oid="6"
 desc="Kill ad servers.">
<attr>http://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
</rewrite>

<rewrite title="Ad servers 07" oid="7"
 desc="Kill links with &apos;banner&apos; in the host name.">
<attr>banner.*\.</attr>
</rewrite>

<block title="Ad servers 08" oid="8"
 desc="matches ad. ads. adserver."
 scheme=""
 host="^ad(s|server)?\."
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Adverts in the path name 01" oid="9"
 desc="Kill links with ad words in the path name.">
<attr>/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
</rewrite>

<rewrite title="Adverts in the path name 02" oid="10"
 desc="Kill links with ad words in the path name.">
<attr>/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew)/</attr>
</rewrite>

<rewrite title="Adverts in the path name 03" oid="11"
 desc="Kill links with ad words in the path name.">
<attr>/event\.ng(\?|/)Type=click</attr>
</rewrite>

<rewrite title="Adverts in the path name 04" oid="12"
 desc="Kill links with ad words in the path name.">
<attr>\.eu-adcenter\.net</attr>
</rewrite>

<block title="CGI adverts 1" oid="13"
 desc="Search for the words &amp;quot;ad&amp;quot; and &amp;quot;click&amp;quot;  in the path and a non-empty query."
 scheme=""
 host=""
 port=""
 path="(ad.*click|click.*thr|click.*ad)"
 parameters=""
 query=".+"
 fragment=""/>

<rewrite title="CGI adverts 2" oid="14"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
</rewrite>

<block title="CGI adverts 3" oid="15"
 desc="Search for advert,banner,adid,profileid in the path."
 scheme=""
 host=""
 port=""
 path="/(advert|banners?|adid|profileid)/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="CGI adverts 4" oid="16"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-acc/clickthru.acc\?</attr>
</rewrite>

<rewrite title="Deja.com adverts" oid="17"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
</rewrite>

<rewrite title="German ad servers" oid="18"
 desc="Kill links with ad words in the host name.">
<attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
</rewrite>

<rewrite title="Heise advert tag" oid="19"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert">
</rewrite>

<rewrite title="Heise advert tag 2" oid="20"
 desc="heise.de"
 tag="contentbanner">
</rewrite>

<block title="Hosts without DNS name" oid="21"
 desc="If a host has no DNS name it consists only of numbers, for  example &amp;quot;http://34.55.124.2&amp;quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images."
 scheme=""
 host="^[\d.]+$"
 port=""
 path=""
 parameters=""
 query="\.gif$"
 fragment=""/>

<rewrite title="Remove &lt;ilayer&gt; tag" oid="22"
 desc="Lots of ads come nowadays in ilayer tags."
 tag="ilayer">
</rewrite>

<rewrite title="Remove &lt;layer&gt; tag" oid="23"
 desc="Dont know some example sites, but I dont want layers."
 tag="layer">
</rewrite>

<rewrite title="Use the &lt;nolayer&gt; tag" oid="24"
 desc="If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content."
 tag="nolayer">
<replace part="tag"/>
</rewrite>

<rewrite title="Userfriendly outbound links" oid="25"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
</rewrite>

<rewrite title="adbouncer" oid="26"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
</rewrite>

<rewrite title="easy-cash" oid="27"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
</rewrite>

<rewrite title="Salon.com" oid="28"
 desc="Jump ads at Salon"
 matchurl="salon.com">
<attr>jump.salon.com</attr>
</rewrite>

<rewrite title="OSDN navbar" oid="29"
 desc="Navigation bar form"
 tag="form">
<attr name="action">http://www\.osdn\.com/osdnsearch\.pl</attr>
</rewrite>

<rewrite title="SF tracker image" oid="30"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
</rewrite>

<rewrite title="IMDB Advert 2" oid="31"
 desc="image map adverts"
 matchurl="imdb"
 tag="area">
<attr>/tiger_redirect\?</attr>
</rewrite>

<rewrite title="IMDB Advert" oid="32"
 desc="adverts are redirections"
 matchurl="imdb">
<attr>/tiger_redirect\?(TITLE_TOP|SUBQS_PROTAWARDS|HOT_IMAGE|HOT_DVD_\d|HOT_VHS_\d|RATINGS|HOME_DVD|GOOFS_TOP|TOPTOP|TOP_BOTTOM|BROWSE|SATURN_SEC_GALLERY|SECGAL_GRANBUT|NURLS_TOP|RTO_SUBSEARCH|MLINKS_RHS)</attr>
</rewrite>

<rewrite title="IMDB Advert 3" oid="33"
 desc="The ultimate solution"
 matchurl="imdb"
 tag="img">
<attr name="usemap">^#m_pro-</attr>
</rewrite>

<rewrite title="Adverts in the path name 7" oid="34">
<attr>/l.click\?clickId=</attr>
</rewrite>

<rewrite title="Onmouseover ads" oid="35"
 desc="This gets rid of the latest generation of JavaScript annoyances. ">
<attr name="onmouseover">parent\.location\s*=</attr>
<replace part="attr"/>
</rewrite>

<rewrite title="IMDB Advert 4" oid="36"
 desc="/r/ stuff and imdb pro"
 matchurl="imdb">
<attr>(/r/|/register/subscribe)</attr>
</rewrite>

<rewrite title="IMDB Advert 5" oid="37"
 desc="Remove ad pics"
 matchurl="imdb"
 tag="img">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</rewrite>

<rewrite title="IMDB Advert 6" oid="38"
 desc="image tag"
 matchurl="imdb"
 tag="image">
<attr name="src">(/Icons/apix/|/apix/celeb/)</attr>
</rewrite>

<rewrite title="EOnline ads" oid="39">
<attr>/cgi-bin/acc_clickthru\?</attr>
</rewrite>

<rewrite title="slashdot ad" oid="40"
 desc="JS ad at slashdot"
 tag="script">
<attr name="src">s0b\.bluestreak\.com</attr>
</rewrite>

<block title="Slashdot JS ad 1" oid="41"
 scheme="http"
 host="images2.slashdot.org"
 port=""
 path="/Slashdot/pc.gif"
 parameters=""
 query=""
 fragment=""/>

<block title="Slashdot JS ad 2" oid="42"
 scheme="http"
 host="images.slashdot.org"
 port=""
 path="/banner/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Atwola JS ad" oid="43"
 desc="found at fortune.com"
 tag="script">
<attr name="src">ar\.atwola\.com</attr>
</rewrite>

<rewrite title="JS .au ad" oid="44"
 desc="Fairfax advert"
 tag="script">
<attr name="src">http://campaigns\.f2\.com\.au</attr>
</rewrite>

<rewrite title="Google Pageads" oid="45"
 desc="Google Javascript (textual) pageads."
 tag="script">
<attr name="src">pagead\.googlesyndication\.com</attr>
</rewrite>

<rewrite title="LWN ad" oid="46"
 desc="Pagead at linux weekly news"
 matchurl="lwn\.net">
<attr>oasis\.lwn\.net/oasisc\.php</attr>
</rewrite>

<rewrite title="Freshmeat ads" oid="47"
 desc="Freshmeat ad server"
 matchurl="freshmeat.net"
 tag="img">
<attr name="src">fmads.osdn.com</attr>
</rewrite>

<rewrite title="MSN ads" oid="125"
 desc="Found at MSN">
<attr>g\.msn(bc)?\.com</attr>
</rewrite>
</folder>
