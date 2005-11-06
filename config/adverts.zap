<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.360" oid="3" configversion="0.10">
<title lang="de">Allgemeine Werbung</title>
<title lang="en">General adverts</title>
<description lang="en">A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href="http://company.com"&gt;&lt;img  src="http://adserver.de/banner.gif"&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.</description>

<htmlrewrite sid="wc.334">
  <title lang="de">Verknüpfungen mit 'ad'</title>
  <title lang="en">Ad servers 01</title>
  <description lang="de">Entferne Verknüpfungen mit dem Wort 'ad' im Rechnernamen.</description>
  <description lang="en">Kill links with 'ad' in the host name.</description>
  <attr>https?://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.344">
  <title lang="de">Verknüpfungen mit 'ad' 2</title>
  <title lang="en">Adverts in the path name 01</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
</htmlrewrite>

<htmlrewrite sid="wc.402">
  <title lang="de">Verknüpfungen mit 'adbouncer'</title>
  <title lang="en">adbouncer</title>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/adbouncer\.phtml</attr>
</htmlrewrite>

<htmlrewrite sid="wc.403">
  <title lang="de">Verknüpfungen mit 'easy-cash'</title>
  <title lang="en">easy-cash</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>easy-cash</attr>
</htmlrewrite>

<htmlrewrite sid="wc.414">
  <title lang="de">Onmouseover Werbung</title>
  <title lang="en">Onmouseover ads</title>
  <description lang="de">Dies entfernt die neueste Kreation der Werbepfuscher.</description>
  <description lang="en">This gets rid of the latest generation of JavaScript annoyances.</description>
  <attr name="onmouseover">parent\.location\s*=</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.336">
  <title lang="de">Verknüpfungen mit 'ads'</title>
  <title lang="en">Ad servers 03</title>
  <description lang="de">Entferne Verknüpfungen mit dem Wort 'ads' im Rechnernamen.</description>
  <attr>https?://(servedby\.)?ad(s|server(\d+)?|vertising)?\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.335">
  <title lang="de">Verknüpfungen mit 'trade' u.a.</title>
  <title lang="en">Ad servers 02</title>
  <description lang="de">Entferne Verknüpfungen mit den Worten 'tradedoubler' 'emerchandise' 'ecommercetimes'</description>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>https?://[^/]*(tradedoubler|emerchandise|ecommercetimes)\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.337">
  <title lang="de">Verknüpfungen mit 'linkexchange' u.a.</title>
  <title lang="en">Ad servers 05</title>
  <description lang="de">Entferne Verknüpfungen mit dem Wort 'linkexchange' u.a. im Rechnernamen.</description>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>https?://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.343">
  <title lang="de">Verknüpfungen mit 'adclick'</title>
  <title lang="en">Ad servers 12</title>
  <description lang="de">Entfernt Verknüpfungen mit dem Wort 'adclick' in der URL.</description>
  <description lang="en">adclick stuff</description>
  <attr>/adclick\.(exe|php)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.345">
  <title lang="de">Verknüpfungen mit 'banner' 2</title>
  <title lang="en">Adverts in the path name 02</title>
  <description lang="de">Entferne Verknüpfungen mit 'banner' u.a. im Pfadnamen.</description>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick)/</attr>
</htmlrewrite>

<htmlrewrite sid="wc.346">
  <title lang="de">Verknüpfungen mit 'event.ng'</title>
  <title lang="en">Adverts in the path name 03</title>
  <description lang="de">Entferne Verknüpfungen mit dem Wort 'event.ng' im Pfad.</description>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>/event\.ng(\?|/)Type=click</attr>
</htmlrewrite>

<htmlrewrite sid="wc.347">
  <title lang="de">Verknüpfungen mit 'eu-adcenter'</title>
  <title lang="en">Adverts in the path name 04</title>
  <description lang="de">Lösche Verknüpfungen mit 'eu-adcenter' im Namen.</description>
  <description lang="en">Kill links with ad words in the path name.</description>
  <attr>\.eu-adcenter\.net</attr>
</htmlrewrite>

<htmlrewrite sid="wc.348">
  <title lang="de">Verknüpfungen mit 'click' u.a.</title>
  <title lang="en">Adverts in the path name 7</title>
  <attr>([\.\?]click\?|click(stream|thrutraffic|thru|xchange)|clickId=|smartserve/click)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.355">
  <title lang="de">Verknüpfungen mit 'werbung' u.a.</title>
  <title lang="en">German adverts</title>
  <description lang="en">Kill links with german ad words in the path.</description>
  <attr>/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
</htmlrewrite>

<htmlrewrite sid="wc.338">
  <title lang="de">Verschiedene Werberechner 1</title>
  <title lang="en">Ad servers 06</title>
  <description lang="de">Entferne Verknüpfungen zu verschiedenen Werberechnern.</description>
  <description lang="en">Kill ad servers.</description>
  <attr>https?://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.342">
  <title lang="de">Verschiedene Werberechner 2</title>
  <title lang="en">Ad servers 11</title>
  <description lang="en">Tribal fusion</description>
  <attr>(a\.tribalfusion\.com|ads\.adcode\.de|www\.bethedealer\.com)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.359">
  <title lang="de">Verschiedene Werberechner 3</title>
  <title lang="en">German ad servers</title>
  <description lang="en">Kill links with ad words in the host name.</description>
  <attr>(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
</htmlrewrite>

<block sid="wc.340"
 url="https?://ad(s|server)?\.">
  <title lang="de">Rechner mit 'ads'</title>
  <title lang="en">Ad servers 08</title>
  <description lang="de">Blockiert Rechner mit 'ads' im Namen.</description>
  <description lang="en">matches url hosts beginning with "ad.", "ads." or "adserver."</description>
</block>

<htmlrewrite sid="wc.341">
  <title lang="de">Rechner mit 'click'</title>
  <title lang="en">Ad servers 10</title>
  <description lang="de">Blockiert Rechner mit 'click' im Namen.</description>
  <description lang="en">Kill links with 'click' words in the host name.</description>
  <attr>https?://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
</htmlrewrite>

<block sid="wc.349"
 url="https?://.*(ad.*click|click.*thr|click.*ad).*\?.+">
  <title lang="de">CGI Werbung mit 'click'</title>
  <title lang="en">CGI adverts 1</title>
  <description lang="en">Search for the words "ad" and "click"  in the path and a non-empty query.</description>
</block>

<htmlrewrite sid="wc.350">
  <title lang="de">CGI Werbung mit 'ads'</title>
  <title lang="en">CGI adverts 2</title>
  <description lang="en">Matches imagess served by CGI and with advert words in the path.</description>
  <attr>/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
</htmlrewrite>

<block sid="wc.351"
 url="https?://.*/(advert|banners?|adid|profileid)/.*\?.*">
  <title lang="de">CGI Werbung mit 'banner' u.a.</title>
  <title lang="en">CGI adverts 3</title>
  <description lang="de">Suche nach advert,banner,adid,profileid in der URL.</description>
  <description lang="en">Search for advert,banner,adid,profileid in the path.</description>
</block>

<htmlrewrite sid="wc.352">
  <title lang="de">CGI Werbung mit 'clickthru'</title>
  <title lang="en">CGI adverts 4</title>
  <description lang="en">Matches imagess served by CGI and with advert words in the path.</description>
  <attr>clickthru.(acc|aspx)\?</attr>
</htmlrewrite>

<block sid="wc.353"
 url="https?://[\d.]+/.*\?.*\.gif">
  <title lang="de">Bilder mit numerischer IP</title>
  <title lang="en">Hosts without DNS name</title>
  <description lang="de">Viele Werbebilder kommen von Rechnern ohne DNS Eintrag.</description>
  <description lang="en">If a host has no DNS name it consists only of numbers, for  example "http://34.55.124.2". A lot of adverts are loaded from such servers. We restrict it further more for CGI queries which fetch GIF images.</description>
</block>

<htmlrewrite sid="wc.356"
 tag="ilayer">
  <title lang="de">Entferne &lt;ilayer&gt;</title>
  <title lang="en">Remove &lt;ilayer&gt; tag</title>
  <description lang="de">Viele Werbungen sind in &lt;ilayer&gt;.</description>
  <description lang="en">Lots of ads come nowadays in ilayer tags.</description>
</htmlrewrite>

<htmlrewrite sid="wc.357"
 tag="layer">
  <title lang="de">Entferne &lt;layer&gt;</title>
  <title lang="en">Remove &lt;layer&gt; tag</title>
  <description lang="de">Layers enthalten meist Werbung.</description>
  <description lang="en">Don't know some example sites, but I don't want layers.</description>
  <nomatchurl>imdb\.com</nomatchurl>
</htmlrewrite>

<htmlrewrite sid="wc.358"
 tag="nolayer">
  <title lang="de">Benutze &lt;nolayer&gt;</title>
  <title lang="en">Use the &lt;nolayer&gt; tag</title>
  <description lang="de">Bei Entfernung von &lt;ilayer&gt; und &lt;layer&gt;, benutze den &lt;nolayer&gt; Inhalt.</description>
  <description lang="en">If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content.</description>
  <nomatchurl>imdb\.com</nomatchurl>
  <replacement part="tag"/>
</htmlrewrite>

<htmlrewrite sid="wc.27">
  <title lang="de">Verknüpfungen mit 'doubleclick'</title>
  <title lang="en">Script adverts</title>
  <description lang="en">JavaScript adverts</description>
  <attr>(double|fast)click\.(net|com)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.34">
  <title lang="de">Verknüpfungen mit buy_assets</title>
  <attr>/buy_assets/</attr>
</htmlrewrite>

<htmlrewrite sid="wc.35">
  <title lang="de">Verknüpfungen mit value</title>
  <attr>value(stream|xchange|click)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.36">
  <title lang="de">Verknüpfungen mit banner</title>
  <attr>(top|bottom|left|right|)?banner(s|id=|\d|_)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.37">
  <title lang="de">Verknüpfungen mit 'dime'</title>
  <attr>dime(xchange|click)</attr>
</htmlrewrite>

<htmlrewrite sid="wc.38">
  <title lang="de">Verknüpfungen mit 'adlog'</title>
  <attr>adlog\.com\.</attr>
</htmlrewrite>

<htmlrewrite sid="wc.52"
 tag="script">
  <title lang="de">JavaScript Werbung</title>
  <description lang="de">JavaScript in HTML von Werberechnern.</description>
  <attr name="src">(adbrite|advertising)\.com</attr>
</htmlrewrite>
</folder>
