<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Advertisements" oid="7"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="/werbung" oid="0"
 desc="Kill links with the german ad word.">
<attr>/werbung</attr>
</rewrite>

<rewrite title="Ad servers 1" oid="1"
 desc="Kill links with ad words in the host name.">
<attr>http://adse?rv.*\.(com|net|de)</attr>
</rewrite>

<rewrite title="Ad servers 10" oid="2">
<attr>(ad\.krutilka\.ru|(fast|double)click\.net|click\.atdmt\.com|ar\.atwola\.com|partners\.webmasterplan\.com|click\.linksynergy\.com|adlog\.com\.com|www\.qksrv\.net)</attr>
</rewrite>

<rewrite title="Ad servers 2" oid="3"
 desc="Kill links with ad words in the host name.">
<attr>(doubleclick|adforce|tradedoubler|netadsrv|adrunner|link4ads|emerchandise|ecommercetimes)\.</attr>
</rewrite>

<rewrite title="Ad servers 3" oid="4"
 desc="Kill links with ad words in the host name.">
<attr>http://ad.*\.flycast\.com</attr>
</rewrite>

<rewrite title="Ad servers 4" oid="5"
 desc="Kill links with ad words in the host name.">
<attr>http://(eur\.)?rd\.yahoo\.com</attr>
</rewrite>

<rewrite title="Ad servers 5" oid="6"
 desc="Kill links with ad words in the host name.">
<attr>((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange|creative-ads|click(it|finders|burst|here.egroups))\.com</attr>
</rewrite>

<rewrite title="Ad servers 6" oid="7"
 desc="Kill links with ad words in the host name.">
<attr>http://ads?\d*?(click)?\..*\.(com|net)</attr>
</rewrite>

<rewrite title="Ad servers 7" oid="8"
 desc="Kill links with ad words in the host name.">
<attr>http://banner.*\.(com|de)</attr>
</rewrite>

<block title="Ad servers 8" oid="9"
 scheme=""
 host="^ads?\."
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Adverts in the path name 1" oid="10"
 desc="Kill links with ad words in the path name.">
<attr>/(web)?ad(vert(s)?|click|s)/</attr>
</rewrite>

<rewrite title="Adverts in the path name 2" oid="11"
 desc="Kill links with ad words in the path name.">
<attr>/(banner(s|_redirect)|clickit|werbung)/</attr>
</rewrite>

<rewrite title="Adverts in the path name 3" oid="12"
 desc="Kill links with ad words in the path name.">
<attr>/event\.ng\?Type=click</attr>
</rewrite>

<rewrite title="Adverts in the path name 4" oid="13"
 desc="Kill links with ad words in the path name.">
<attr>\.eu-adcenter\.net</attr>
</rewrite>

<rewrite title="Adverts in the path name 5" oid="14"
 desc="Found at debianhelp.org"
 tag="img">
<attr name="src">/images/vbanners</attr>
</rewrite>

<block title="Adverts in the path name 6" oid="15"
 desc="the infamous realmedia ads"
 scheme=""
 host=""
 port=""
 path="/RealMedia/"
 parameters=""
 query=""
 fragment=""/>

<image title="Banner at rootprompt.org" oid="16"
 desc="The website rootprompt.org has a banner image."
 matchurl="rootprompt\.org"
 width="465"
 height="58"/>

<block title="CGI adverts 1" oid="17"
 desc="Search for the words &amp;quot;ad&amp;quot; and &amp;quot;click&amp;quot;  in the path and a non-empty query."
 scheme=""
 host=""
 port=""
 path="(ad.*click|click.*thr|click.*ad)"
 parameters=""
 query=".+"
 fragment=""/>

<rewrite title="CGI adverts 2" oid="18"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
</rewrite>

<block title="CGI adverts 3" oid="19"
 desc="Search for advert,banner,adid,profileid in the path."
 scheme=""
 host=""
 port=""
 path="/(advert|banners?|adid|profileid)/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="CGI adverts 4" oid="20"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-acc/clickthru.acc\?</attr>
</rewrite>

<rewrite title="CGI adverts 5" oid="21"
 desc="Kill links with ad words in the path name.">
<attr>/cgi-bin/bannerclick</attr>
</rewrite>

<rewrite title="Deja.com adverts" oid="22"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
</rewrite>

<rewrite title="German ad servers" oid="23"
 desc="Kill links with ad words in the host name.">
<attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
</rewrite>

<rewrite title="Heise advert tag" oid="24"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert">
</rewrite>

<rewrite title="Heise advert tag 2" oid="25"
 desc="heise.de"
 tag="contentbanner">
</rewrite>

<block title="Hosts without DNS name" oid="26"
 desc="If a host has no DNS name it consists only of numbers, for  example &amp;quot;http://34.55.124.2&amp;quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images."
 scheme=""
 host="^[\d.]+$"
 port=""
 path=""
 parameters=""
 query="\.gif$"
 fragment=""/>

<rewrite title="Remove &lt;ilayer&gt; tag" oid="27"
 desc="Lots of ads come nowadays in ilayer tags."
 tag="ilayer">
</rewrite>

<rewrite title="Remove &lt;layer&gt; tag" oid="28"
 desc="Dont know some example sites, but I dont want layers."
 tag="layer">
</rewrite>

<rewrite title="Use the &lt;nolayer&gt; tag" oid="29"
 desc="If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content."
 tag="nolayer">
<replace part="tag"/>
</rewrite>

<rewrite title="Userfriendly outbound links" oid="30"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
</rewrite>

<rewrite title="adbouncer" oid="31"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
</rewrite>

<rewrite title="easy-cash" oid="32"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
</rewrite>

<rewrite title="Salon.com" oid="33"
 desc="Jump ads at Salon"
 matchurl="salon.com">
<attr>jump.salon.com</attr>
</rewrite>

<rewrite title="OSDN navbar" oid="34"
 desc="Navigation bar form"
 tag="form">
<attr name="action">http://www\.osdn\.com/osdnsearch\.pl</attr>
</rewrite>

<rewrite title="SF tracker image" oid="35"
 desc="akamai tracker image at sourceforge"
 tag="img">
<attr name="src">e\.akamai\.net</attr>
</rewrite>

<rewrite title="IMDB Advert 2" oid="36"
 desc="image map adverts"
 matchurl="imdb"
 tag="area">
<attr>/tiger_redirect\?</attr>
</rewrite>

<rewrite title="IMDB Advert" oid="37"
 desc="adverts are redirections"
 matchurl="imdb">
<attr>/tiger_redirect\?</attr>
</rewrite>

<rewrite title="IMDB Advert 3" oid="38"
 desc="The ultimate solution"
 matchurl="imdb"
 tag="img">
<attr name="usemap">^#m_pro-</attr>
</rewrite>
</folder>
