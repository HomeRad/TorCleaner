<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.360" oid="3">
<title lang="de">Allgemeine Werbung</title>
<title lang="en">General adverts</title>
<description lang="en">A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href=&amp;quot;http://company.com&amp;quot;&gt;&lt;img  src=&amp;quot;http://adserver.de/banner.gif&amp;quot;&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.</description>

<rewrite sid="wc.334">
  <title lang="en">Ad servers 01</title>
  <description lang="de">Entferne Verknuepfungen mit dem Wort &apos;ad&apos; im Rechnernamen.</description>
  <description lang="en">Kill links with &apos;ad&apos; in the host name.</description>
  <attr>https?://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
</rewrite>

<rewrite sid="wc.335">
  <title lang="en">Ad servers 02</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>https?://[^/]*(tradedoubler|emerchandise|ecommercetimes)\.</attr>
</rewrite>

<rewrite sid="wc.336">
  <title lang="en">Ad servers 03</title>
  <attr>https?://ad(s|server)?\.</attr>
</rewrite>

<rewrite sid="wc.337">
  <title lang="en">Ad servers 05</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>https?://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
</rewrite>

<rewrite sid="wc.338">
  <title lang="en">Ad servers 06</title>
  <description lang="en">Kill ad servers.</description>
  <attr>https?://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
</rewrite>

<rewrite sid="wc.339">
  <title lang="en">Ad servers 07</title>
  <description lang="en">Kill links with &apos;banner&apos; in the host name.</description>
  <attr>banner.*\.</attr>
</rewrite>

<block sid="wc.340"
 url="https?://ad(s|server)?\.">
  <title lang="en">Ad servers 08</title>
  <description lang="en">matches url hosts beginning with &amp;quot;ad.&amp;quot;, &amp;quot;ads.&amp;quot; or &amp;quot;adserver.&amp;quot;</description>
</block>

<rewrite sid="wc.341">
  <title lang="en">Ad servers 10</title>
  <description lang="en">Kill links with &apos;click&apos; words in the host name.</description>
  <attr>https?://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
</rewrite>

<rewrite sid="wc.342">
  <title lang="en">Ad servers 11</title>
  <description lang="en">Tribal fusion</description>
  <attr>(a\.tribalfusion\.com|ads\.adcode\.de|www\.bethedealer\.com)</attr>
</rewrite>

<rewrite sid="wc.343">
  <title lang="en">Ad servers 12</title>
  <description lang="en">adclick stuff</description>
  <attr>/adclick\.(exe|php)</attr>
</rewrite>

<block sid="wc.2"
 url="https?://ad(s|server)?\.">
  <title lang="en">Ad servers 13</title>
</block>

<rewrite sid="wc.344">
  <title lang="en">Adverts in the path name 01</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
</rewrite>

<rewrite sid="wc.345">
  <title lang="en">Adverts in the path name 02</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick)/</attr>
</rewrite>

<rewrite sid="wc.346">
  <title lang="en">Adverts in the path name 03</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/event\.ng(\?|/)Type=click</attr>
</rewrite>

<rewrite sid="wc.347">
  <title lang="en">Adverts in the path name 04</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>\.eu-adcenter\.net</attr>
</rewrite>

<rewrite sid="wc.348">
  <title lang="en">Adverts in the path name 7</title>
  <attr>(l.click\?clickId=|smartserve/click)</attr>
</rewrite>

<block sid="wc.349"
 url="https?://.*(ad.*click|click.*thr|click.*ad).*\?.+">
  <title lang="en">CGI adverts 1</title>
  <description lang="en">Search for the words &amp;quot;ad&amp;quot; and &amp;quot;click&amp;quot;  in the path and a non-empty query.</description>
</block>

<rewrite sid="wc.350">
  <title lang="en">CGI adverts 2</title>
  <description lang="en">Matches imagess served by CGI and with advert words in the path.</description>
  <attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
</rewrite>

<block sid="wc.351"
 url="https?://.*/(advert|banners?|adid|profileid)/">
  <title lang="en">CGI adverts 3</title>
  <description lang="en">Search for advert,banner,adid,profileid in the path.</description>
</block>

<rewrite sid="wc.352">
  <title lang="en">CGI adverts 4</title>
  <description lang="en">Matches imagess served by CGI and with advert words in the path.</description>
  <attr>clickthru.(acc|aspx)\?</attr>
</rewrite>

<block sid="wc.353"
 url="https?://[\d.]+/.*\?.*\.gif">
  <title lang="en">Hosts without DNS name</title>
  <description lang="en">If a host has no DNS name it consists only of numbers, for  example &amp;quot;http://34.55.124.2&amp;quot;. A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images.</description>
</block>

<rewrite sid="wc.354">
  <title lang="en">Counter and tracker</title>
  <description lang="en">Kill tracker and counter cgi scripts.</description>
  <attr>/.*(count|track)(er|run)?\.(pl|cgi|exe|dll|asp|php[34]?)</attr>
</rewrite>

<rewrite sid="wc.355">
  <title lang="en">German adverts</title>
  <description lang="en">Kill links with german ad words in the path.</description>
  <attr>/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
</rewrite>

<rewrite sid="wc.356"
 tag="ilayer">
  <title lang="en">Remove &lt;ilayer&gt; tag</title>
  <description lang="en">Lots of ads come nowadays in ilayer tags.</description>
</rewrite>

<rewrite sid="wc.357"
 tag="layer">
  <title lang="en">Remove &lt;layer&gt; tag</title>
  <description lang="en">Don&apos;t know some example sites, but I don&apos;t want layers.</description>
</rewrite>

<rewrite sid="wc.358"
 tag="nolayer">
  <title lang="en">Use the &lt;nolayer&gt; tag</title>
  <description lang="en">If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content.</description>
  <replacement part="tag"/>
</rewrite>

<rewrite sid="wc.359">
  <title lang="en">German ad servers</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
</rewrite>
</folder>
