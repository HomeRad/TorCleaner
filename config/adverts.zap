<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.360" title="General adverts"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it." oid="0">
<rewrite sid="wc.334" title="Ad servers 01"
 desc="Kill links with &apos;ad&apos; in the host name.">
<attr>https?://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.335" title="Ad servers 02"
 desc="Kill links with ad words in the host name.">
<attr>https?://[^/]*(tradedoubler|emerchandise|ecommercetimes)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.336" title="Ad servers 03">
<attr>https?://ad(s|server)?\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.337" title="Ad servers 05"
 desc="Kill links with ad words in the host name.">
<attr>https?://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.338" title="Ad servers 06"
 desc="Kill ad servers.">
<attr>https?://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.339" title="Ad servers 07"
 desc="Kill links with &apos;banner&apos; in the host name.">
<attr>banner.*\.</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.340" title="Ad servers 08"
 desc="matches url hosts beginning with &amp;quot;ad.&amp;quot;, &amp;quot;ads.&amp;quot; or &amp;quot;adserver.&amp;quot;"
 url="https?://ad(s|server)?\."/>

<rewrite sid="wc.341" title="Ad servers 10"
 desc="Kill links with &apos;click&apos; words in the host name.">
<attr>https?://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.342" title="Ad servers 11"
 desc="Tribal fusion">
<attr>(a\.tribalfusion\.com|ads\.adcode\.de|www\.bethedealer\.com)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.343" title="Ad servers 12"
 desc="adclick stuff">
<attr>/adclick\.(exe|php)</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.2" title="Ad servers 13"
 url="https?://ad(s|server)?\."/>

<rewrite sid="wc.344" title="Adverts in the path name 01"
 desc="Kill links with ad words in the path name.">
<attr>/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.345" title="Adverts in the path name 02"
 desc="Kill links with ad words in the path name.">
<attr>/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.346" title="Adverts in the path name 03"
 desc="Kill links with ad words in the path name.">
<attr>/event\.ng(\?|/)Type=click</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.347" title="Adverts in the path name 04"
 desc="Kill links with ad words in the path name.">
<attr>\.eu-adcenter\.net</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.348" title="Adverts in the path name 7">
<attr>(l.click\?clickId=|smartserve/click)</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.349" title="CGI adverts 1"
 desc="Search for the words &amp;quot;ad&amp;quot; and &amp;quot;click&amp;quot;  in the path and a non-empty query."
 url="https?://.*(ad.*click|click.*thr|click.*ad).*\?.+"/>

<rewrite sid="wc.350" title="CGI adverts 2"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.351" title="CGI adverts 3"
 desc="Search for advert,banner,adid,profileid in the path."
 url="https?://.*/(advert|banners?|adid|profileid)/"/>

<rewrite sid="wc.352" title="CGI adverts 4"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>clickthru.(acc|aspx)\?</attr>
<replacement part="complete"/>
</rewrite>

<block sid="wc.353" title="Hosts without DNS name"
 desc="If a host has no DNS name it consists only of numbers, for  example &amp;quot;http://34.55.124.2&amp;quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images."
 url="https?://[\d.]+/.*\?.*\.gif"/>

<rewrite sid="wc.354" title="Counter and tracker"
 desc="Kill tracker and counter cgi scripts.">
<attr>/.*(count|track)(er|run)?\.(pl|cgi|exe|dll|asp|php[34]?)</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.355" title="/werbung"
 desc="Kill links with the german ad word in the path.">
<attr>/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.356" title="Remove &lt;ilayer&gt; tag"
 desc="Lots of ads come nowadays in ilayer tags."
 dontmatchurl="www\.mplayerhq\.hu"
 tag="ilayer"/>


<rewrite sid="wc.357" title="Remove &lt;layer&gt; tag"
 desc="Don&apos;t know some example sites, but I dont want layers."
 dontmatchurl="www\.on2\.com|www\.mplayerhq\.hu|\.imdb\.com|www\.spielen-lernen-bewegen\.de"
 tag="layer"/>


<rewrite sid="wc.358" title="Use the &lt;nolayer&gt; tag"
 desc="If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content."
 tag="nolayer">
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.359" title="German ad servers"
 desc="Kill links with ad words in the host name.">
<attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
<replacement part="complete"/>
</rewrite>
</folder>
