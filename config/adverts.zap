<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Advertisements"
 desc="A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&quot;http://company.com&quot;&gt;&lt;img  src=&quot;http://adserver.de/banner.gif&quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.">

<rewrite title="/werbung"
 desc="Kill links with the german ad word.">
<attr>/werbung</attr>
</rewrite>

<rewrite title="Ad servers 1"
 desc="Kill links with ad words in the host name.">
<attr>http://adse?rv.*\.(com|net)</attr>
</rewrite>

<rewrite title="Ad servers 2"
 desc="Kill links with ad words in the host name.">
<attr>http://.*(doubleclick|adforce|tradedoubler|netadsrv|adrunner)\.</attr>
</rewrite>

<rewrite title="Ad servers 3"
 desc="Kill links with ad words in the host name.">
<attr>http://ad.*\.flycast\.com</attr>
</rewrite>

<rewrite title="Ad servers 4"
 desc="Kill links with ad words in the host name.">
<attr>http://(eur\.)?rd\.yahoo\.com</attr>
</rewrite>

<rewrite title="Ad servers 5"
 desc="Kill links with ad words in the host name.">
<attr>((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange|creative-ads|click(it|finders|burst|here.egroups))\.com</attr>
</rewrite>

<rewrite title="Ad servers 6"
 desc="Kill links with ad words in the host name.">
<attr>http://ads?\d*?(click)?\..*\.(com|net)</attr>
</rewrite>

<rewrite title="Ad servers 7"
 desc="Kill links with ad words in the host name.">
<attr>http://banner.*\.(com|de)</attr>
</rewrite>

<rewrite title="Adverts in the path name 1"
 desc="Kill links with ad words in the path name.">
<attr>/(web)?ad(vert(s)?|click|s/)</attr>
</rewrite>

<rewrite title="Adverts in the path name 2"
 desc="Kill links with ad words in the path name.">
<attr>/(banner(s|_redirect)|clickit|werbung)/</attr>
</rewrite>

<rewrite title="Adverts in the path name 3"
 desc="Kill links with ad words in the path name.">
<attr>/event\.ng\?Type=click</attr>
</rewrite>

<rewrite title="Adverts in the path name 4"
 desc="Kill links with ad words in the path name.">
<attr>\.eu-adcenter\.net</attr>
</rewrite>

<rewrite title="Adverts in the path name 5"
 desc="Found at debianhelp.org"
 tag="img">
<attr name="src">/images/vbanners</attr>
</rewrite>

<image title="Banner at rootprompt.org"
 desc="The website rootprompt.org has a banner image."
 width="465"
 height="58"/>

<block title="CGI adverts 1"
 desc="Search for the words &quot;ad&quot; and &quot;click&quot;  in the path and a non-empty query."
 scheme=""
 host=""
 port=""
 path="(ad.*click|click.*thr|click.*ad)"
 parameters=""
 query=".+"
 fragment=""/>

<rewrite title="CGI adverts 2"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-bin/ads?(log)?.*([=&amp;?]|\.gif)</attr>
</rewrite>

<block title="CGI adverts 3"
 desc="Search for advert,banner,adid,profileid in the path."
 scheme=""
 host=""
 port=""
 path="(advert|banner|adid|profileid)"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="CGI adverts 4"
 desc="This rule matches GIFs served by CGI and with advert words in the path.">
<attr>/cgi-acc/clickthru.acc\?</attr>
</rewrite>

<rewrite title="CGI adverts 5"
 desc="Kill links with ad words in the path name.">
<attr>/cgi-bin/bannerclick</attr>
</rewrite>

<rewrite title="Deja.com adverts"
 desc="Kill links with ad words in the host name.">
<attr>www\.deja\.com/jump/</attr>
</rewrite>

<rewrite title="German ad servers"
 desc="Kill links with ad words in the host name.">
<attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
</rewrite>

<rewrite title="Heise advert tag"
 desc="www.heise.de has an advert tag. Nice :)"
 tag="heiseadvert">
</rewrite>

<rewrite title="Heise advert tag 2"
 desc="heise.de"
 tag="contentbanner">
</rewrite>

<block title="Hosts without DNS name"
 desc="If a host has no DNS name it consists only of numbers, for  example &quot;http://34.55.124.2&quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images."
 scheme=""
 host="^[\d.]+$"
 port=""
 path=""
 parameters=""
 query="\.gif$"
 fragment=""/>

<rewrite title="Remove &lt;ilayer&gt; tag"
 desc="Lots of ads come nowadays in ilayer tags."
 tag="ilayer">
</rewrite>

<rewrite title="Remove &lt;layer&gt; tag"
 desc="Dont know some example sites, but I dont want layers."
 tag="layer">
</rewrite>

<rewrite title="Use the &lt;nolayer&gt; tag"
 desc="If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content."
 tag="nolayer">
<replace part="tag"/>
</rewrite>

<rewrite title="Userfriendly outbound links"
 desc="Links on userfriendly.org which point outbound. This is a redirector host.">
<attr>http://links\.userfriendly\.org</attr>
</rewrite>

<rewrite title="adbouncer"
 desc="Kill links with ad words in the path name.">
<attr>/adbouncer\.phtml</attr>
</rewrite>

<rewrite title="easy-cash"
 desc="Kill links with ad words in the host name.">
<attr>easy-cash</attr>
</rewrite>
</folder>