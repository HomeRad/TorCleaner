<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Adverts" oid="0"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="Ad servers 01" oid="0"
 desc="Kill links with &apos;ad&apos; in the host name.">
<attr>http://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 02" oid="1"
 desc="Kill links with ad words in the host name.">
<attr>http://[^/]*(tradedoubler|emerchandise|ecommercetimes)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 03" oid="2">
<attr>http://ad(s|server)?\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 05" oid="3"
 desc="Kill links with ad words in the host name.">
<attr>http://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 06" oid="4"
 desc="Kill ad servers.">
<attr>http://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 07" oid="5"
 desc="Kill links with &apos;banner&apos; in the host name.">
<attr>banner.*\.</attr>
<replacement part="complete"/>
</rewrite>

<block title="Ad servers 08" oid="6"
 desc="matches ad. ads. adserver."
 scheme=""
 host="^ad(s|server)?\."
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Ad servers 10" oid="7"
 desc="Kill links with &apos;click&apos; words in the host name.">
<attr>http://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 11" oid="8"
 desc="Tribal fusion">
<attr>a\.tribalfusion\.com</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Ad servers 12" oid="9"
 desc="adclick stuff">
<attr>/adclick\.(exe|php)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Adverts in the path name 01" oid="10"
 desc="Kill links with ad words in the path name.">
<attr>/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Adverts in the path name 02" oid="11"
 desc="Kill links with ad words in the path name.">
<attr>/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Adverts in the path name 03" oid="12"
 desc="Kill links with ad words in the path name.">
<attr>/event\.ng(\?|/)Type=click</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Adverts in the path name 04" oid="13"
 desc="Kill links with ad words in the path name.">
<attr>\.eu-adcenter\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Adverts in the path name 7" oid="14">
<attr>(l.click\?clickId=|smartserve/click)</attr>
<replacement part="complete"/>
</rewrite>

<block title="CGI adverts 1" oid="15"
 desc="Search for the words &amp;quot;ad&amp;quot; and &amp;quot;click&amp;quot;  in the path and a non-empty query."
 scheme=""
 host=""
 port=""
 path="(ad.*click|click.*thr|click.*ad)"
 parameters=""
 query=".+"
 fragment=""/>

<rewrite title="CGI adverts 2" oid="16"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
<replacement part="complete"/>
</rewrite>

<block title="CGI adverts 3" oid="17"
 desc="Search for advert,banner,adid,profileid in the path."
 scheme=""
 host=""
 port=""
 path="/(advert|banners?|adid|profileid)/"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="CGI adverts 4" oid="18"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>clickthru.(acc|aspx)\?</attr>
<replacement part="complete"/>
</rewrite>

<block title="Hosts without DNS name" oid="19"
 desc="If a host has no DNS name it consists only of numbers, for  example &amp;quot;http://34.55.124.2&amp;quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images."
 scheme=""
 host="^[\d.]+$"
 port=""
 path=""
 parameters=""
 query="\.gif$"
 fragment=""/>

<rewrite title="Counter and tracker" oid="20"
 desc="Kill tracker and counter cgi scripts.">
<attr>/.*(count|track)(er|run)?\.(pl|cgi|exe|dll|asp|php[34]?)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="/werbung" oid="21"
 desc="Kill links with the german ad word in the path.">
<attr>/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite title="Remove &lt;ilayer&gt; tag" oid="22"
 desc="Lots of ads come nowadays in ilayer tags."
 dontmatchurl="www\.mplayerhq\.hu"
 tag="ilayer"/>


<rewrite title="Remove &lt;layer&gt; tag" oid="23"
 desc="Dont know some example sites, but I dont want layers."
 dontmatchurl="www\.on2\.com|www\.mplayerhq\.hu"
 tag="layer"/>


<rewrite title="Use the &lt;nolayer&gt; tag" oid="24"
 desc="If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content."
 tag="nolayer">
<replacement part="tag"/>
</rewrite>

<rewrite title="German ad servers" oid="25"
 desc="Kill links with ad words in the host name.">
<attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
<replacement part="complete"/>
</rewrite>
</folder>
