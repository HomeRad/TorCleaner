<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.360" oid="3" configversion="0.10">
<title lang="de">Allgemeine Werbung</title>
<title lang="en">General adverts</title>
<description lang="en">A lot of web sites have advertisments. The typical advert has an anchor tag and included the advert image:  &lt;a href="http://company.com"&gt;&lt;img  src="http://adserver.de/banner.gif"&gt;&lt;a&gt;.  So we search for the &lt;a&gt; tag and remove it.</description>

<htmlrewrite sid="wc.334"
 tag="a">
  <title lang="de">Rechner mit 'ad'</title>
  <title lang="en">Host with 'ad'</title>
  <description lang="de">Entferne Verknüpfungen mit dem Wort 'ad' im Rechnernamen.</description>
  <description lang="en">Remove links with 'ad' in the host name.</description>
  <attr name="href">https?://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.344"
 tag="a">
  <title lang="de">Verknüpfungen mit 'ad'</title>
  <title lang="en">Links with 'ad'</title>
  <description lang="de">Entferne Verknüpfungen mit 'ad' im Pfad.</description>
  <description lang="en">Remove links with ad words in the path name.</description>
  <attr name="href">/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.402"
 tag="a">
  <title lang="de">Verknüpfungen mit 'adbouncer'</title>
  <title lang="en">Links with 'adbouncer'</title>
  <description lang="de">Entferne Verknüpfungen mit 'adbouncer' im Pfad.</description>
  <description lang="en">Remove links with 'adbouncer' in the path name.</description>
  <attr name="href">/adbouncer\.phtml</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.403"
 tag="a">
  <title lang="de">Verknüpfungen mit 'easy-cash'</title>
  <title lang="en">Links with 'easy-cash'</title>
  <description lang="de">Entferne Verknüpfungen mit 'easy-cash' im Rechnernamen.</description>
  <description lang="en">Remove links with 'easy-cash' in the host name.</description>
  <attr name="href">easy-cash|/jsads/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.414"
 tag="a">
  <title lang="de">Onmouseover Werbung</title>
  <title lang="en">Onmouseover ads</title>
  <description lang="de">Entfernt JavaScript Werbung.</description>
  <description lang="en">Gets rid of JavaScript annoyances.</description>
  <attr name="onmouseover">parent\.location\s*=</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.336"
 tag="a">
  <title lang="de">Verknüpfungen mit 'ads'</title>
  <title lang="en">Links with 'ads'</title>
  <description lang="de">Entferne Verknüpfungen mit 'ads' im Rechnernamen.</description>
  <description lang="en">Remove links with 'ads' in the host name.</description>
  <attr name="href">https?://(servedby\.)?ad(s|server(\d+)?|vertising)?\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.335"
 tag="a">
  <title lang="de">Verknüpfungen mit 'trade' u.a.</title>
  <title lang="en">Links with 'trade' etc.</title>
  <description lang="de">Entferne Verknüpfungen mit 'trade' und weiteren im Rechnernamen.</description>
  <description lang="en">Remove links with 'trade' and others in the host name.</description>
  <attr name="href">https?://[^/]*(tradedoubler|emerchandise|ecommercetimes|ivwbox)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.337"
 tag="a">
  <title lang="de">Verknüpfungen mit 'linkexchange' u.a.</title>
  <title lang="en">Links with 'linkexchange' etc.</title>
  <description lang="de">Entferne Verknüpfungen mit 'linkexchange' und weiteren im Rechnernamen.</description>
  <description lang="en">Remove links with 'linkexchange' and others in the host name.</description>
  <attr name="href">https?://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.343"
 tag="a">
  <title lang="de">Verknüpfungen mit 'adclick'</title>
  <title lang="en">Links with 'adclick'</title>
  <description lang="de">Entferne Verknüpfungen mit 'adclick' im Pfad.</description>
  <description lang="en">Remove links with 'adlink' in the path.</description>
  <attr name="href">/adclick\.(exe|php)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.345"
 tag="a">
  <title lang="de">Verknüpfungen mit 'banner' u.a.</title>
  <title lang="en">Links with 'banner' etc.</title>
  <description lang="de">Entferne Verknüpfungen mit 'banner' und weiteren im Pfad.</description>
  <description lang="en">Remove links with 'banner' and others in the path.</description>
  <attr name="href">/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick|AdServer)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.346"
 tag="a">
  <title lang="de">Verknüpfungen mit 'event.ng'</title>
  <title lang="en">Links with 'event.ng'</title>
  <description lang="de">Entferne Verknüpfungen mit 'event.ng' im Pfad.</description>
  <description lang="en">Remove links with 'event.ng' in the path.</description>
  <attr name="href">/event\.ng(\?|/)Type=click</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.347"
 tag="a">
  <title lang="de">Verknüpfungen mit 'eu-adcenter'</title>
  <title lang="en">Links with 'eu-adcenter'</title>
  <description lang="de">Lösche Verknüpfungen mit 'eu-adcenter' im Namen.</description>
  <description lang="en">Remove links with 'eu-adcenter' in the path.</description>
  <attr name="href">\.eu-adcenter\.net</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.348"
 tag="a">
  <title lang="de">Verknüpfungen mit 'click'</title>
  <title lang="en">Links mit 'click'</title>
  <description lang="de">Remove links with 'click' in the path.</description>
  <attr name="href">([\.\?]click[\?=]|click(stream|thrutraffic|thru|xchange)|clickId=|smartserve/click)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.355"
 tag="a">
  <title lang="de">Verknüpfungen mit 'werbung' u.a.</title>
  <title lang="en">Links with 'werbung' etc.</title>
  <description lang="de">Lösche Verknüpfungen mit 'werbung' und weiteren im Namen.</description>
  <description lang="en">Remove links with 'werbung' and others in the path.</description>
  <attr name="href">/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.338"
 tag="a">
  <title lang="de">Verknüpfungen zu Werberechnern 1</title>
  <title lang="en">Links to ad servers 1</title>
  <description lang="de">Entferne Verknüpfungen zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove links to some ad servers.</description>
  <attr name="href">https?://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.342"
 tag="a">
  <title lang="de">Verknüpfungen zu Werberechnern 2</title>
  <title lang="en">Links to ad servers 2</title>
  <description lang="de">Entferne Verknüpfungen zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove links to some ad servers.</description>
  <attr name="href">(a\.tribalfusion\.com|ads\.adcode\.de|www\.bethedealer\.com|www\.cpadeal\.com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.359"
 tag="a">
  <title lang="de">Verknüpfungen zu Werberechnern 3</title>
  <title lang="en">Links to ad servers 3</title>
  <description lang="de">Entferne Verknüpfungen zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove links to some ad servers.</description>
  <attr name="href">(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity|zanox-affiliate)\.de</attr>
  <replacement part="complete"/>
</htmlrewrite>

<block sid="wc.340"
 url="https?://(layer-)?ad(s|server)?\.">
  <title lang="de">Rechner mit 'ads'</title>
  <title lang="en">Ad servers with 'ads'</title>
  <description lang="de">Blockiert Rechner mit 'ads' im Namen.</description>
  <description lang="en">matches url hosts beginning with "ad.", "ads." or "adserver."</description>
</block>

<htmlrewrite sid="wc.341"
 tag="a">
  <title lang="de">Rechner mit 'click'</title>
  <title lang="en">Ad servers 10</title>
  <description lang="de">Blockiert Rechner mit 'click' im Namen.</description>
  <description lang="en">Remove links with 'click' words in the host name.</description>
  <attr name="href">https?://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups|s\.totemcash))\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<block sid="wc.349"
 url="https?://.*(ad.*click|click.*thr|click.*ad).*\?.+">
  <title lang="de">CGI Werbung mit 'click'</title>
  <title lang="en">CGI adverts with 'click'</title>
  <description lang="de">Blocke Rechner mit 'ad' und 'click' im Namen.</description>
  <description lang="en">Block hosts with 'ad' and 'click'  in the path.</description>
</block>

<htmlrewrite sid="wc.350"
 tag="a">
  <title lang="de">CGI Werbung mit 'ads'</title>
  <title lang="en">CGI adverts with 'ads'</title>
  <description lang="de">Lösche Verknüpfungen mit 'ads' im CGI Namen.</description>
  <description lang="en">Remove links with 'ads' in the CGI path.</description>
  <attr name="href">/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
  <replacement part="complete"/>
</htmlrewrite>

<block sid="wc.351"
 url="https?://.*/(advert|banners?|adid|profileid)/.*\?.*">
  <title lang="de">CGI Werbung mit 'banner' u.a.</title>
  <title lang="en">CGI adverts with 'banner' etc.</title>
  <description lang="de">Blocke Rechner mit 'banner' und weiteren im Namen.</description>
  <description lang="en">Block hosts with 'banner' and others in the path.</description>
</block>

<htmlrewrite sid="wc.352"
 tag="a">
  <title lang="de">CGI Werbung mit 'clickthru'</title>
  <title lang="en">CGI adverts with 'clickthru'</title>
  <description lang="de">Lösche Verknüpfungen mit 'clickthru' im CGI Namen.</description>
  <description lang="en">Remove links with 'clickthru' in the CGI path.</description>
  <attr name="href">clickthru.(acc|aspx)\?</attr>
  <replacement part="complete"/>
</htmlrewrite>

<block sid="wc.353"
 url="https?://[\d.]+/.*\?.*\.gif">
  <title lang="de">Bilder mit numerischer IP</title>
  <title lang="en">Images with numeric IP</title>
  <description lang="de">Einige Werbebilder kommen von Rechnern ohne DNS Eintrag.</description>
  <description lang="en">Some adverts are loaded from servers with numeric IP.</description>
</block>

<htmlrewrite sid="wc.356"
 tag="ilayer">
  <title lang="de">Entferne &lt;ilayer&gt;</title>
  <title lang="en">Remove &lt;ilayer&gt; tag</title>
  <description lang="de">Einige Werbungen sind in &lt;ilayer&gt;.</description>
  <description lang="en">Some ads come nowadays in ilayer tags.</description>
  <matchurl>dummy\.com</matchurl>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.357"
 tag="layer">
  <title lang="de">Entferne &lt;layer&gt;</title>
  <title lang="en">Remove &lt;layer&gt; tag</title>
  <description lang="de">Einige Layers enthalten Werbung.</description>
  <description lang="en">Some layers have ads.</description>
  <matchurl>dummy\.com</matchurl>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.358"
 tag="nolayer">
  <title lang="de">Benutze &lt;nolayer&gt;</title>
  <title lang="en">Use the &lt;nolayer&gt; tag</title>
  <description lang="de">Bei Entfernung von &lt;ilayer&gt; und &lt;layer&gt;, benutze den &lt;nolayer&gt; Inhalt.</description>
  <description lang="en">If we remove the &lt;ilayer&gt; and &lt;layer&gt;, use the &lt;nolayer&gt; content.</description>
  <matchurl>dummy\.com</matchurl>
  <replacement part="tag"/>
</htmlrewrite>

<htmlrewrite sid="wc.27"
 tag="a">
  <title lang="de">Entferne verknüpfungen mit 'doubleclick'</title>
  <title lang="en">Remove links with 'doubleclick'</title>
  <description lang="de">Entferne Verknüpfungen mit 'doubleclick' im Rechnernamen.</description>
  <description lang="en">Remove links with 'doubleclick' in the host name.</description>
  <attr name="href">(double|fast)click\.(net|com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.34"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'buy_assets'</title>
  <title lang="en">Remove links with 'buy_assets'</title>
  <description lang="de">Entferne Verknüpfungen mit 'buy_assets' im Namen.</description>
  <description lang="en">Remove links with 'buy_assets' in the name.</description>
  <attr name="href">/buy_assets/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.35"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'value'</title>
  <title lang="en">Remove links with 'value'</title>
  <description lang="de">Entferne Verknüpfungen mit 'value' im Namen.</description>
  <description lang="en">Remove links with 'value' in the name.</description>
  <attr name="href">value(stream|xchange|click)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.36"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'banner'</title>
  <title lang="en">Remove links with 'banner'</title>
  <description lang="de">Entferne Verknüpfungen mit 'banner' im Namen.</description>
  <description lang="en">Remove links with 'banner' in the name.</description>
  <attr name="href">(top|bottom|left|right|)?banner(s|id=|\d|_)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.37"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'dime'</title>
  <title lang="en">Remove links with 'dime'</title>
  <description lang="de">Entferne Verknüpfungen mit 'dime' im Namen.</description>
  <description lang="en">Remove links with 'dime' in the name.</description>
  <attr name="href">dime(xchange|click)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.38"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'adlog'</title>
  <title lang="en">Remove links with 'adlog'</title>
  <description lang="de">Entferne Verknüpfungen mit 'adlog' im Namen.</description>
  <description lang="en">Remove links with 'adlog' in the name.</description>
  <attr name="href">adlog\.com\.|survey\.questionmarket\.com</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.85"
 tag="a">
  <title lang="de">Entferne Verknüpfungen mit 'adid'</title>
  <title lang="en">Remove links with 'adid'</title>
  <description lang="de">Entferne Verknüpfungen mit 'adid' im Namen.</description>
  <description lang="en">Remove links with 'adid' in the name.</description>
  <attr name="href">obidos/redirect\?.*adid=.+</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.52"
 tag="iframe|script">
  <title lang="de">Rechner mit 'ad'</title>
  <title lang="en">Host with 'ad'</title>
  <description lang="de">Entferne frames/scripts mit dem Wort 'ad' im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'ad' in the host name.</description>
  <attr name="src">https?://([^/])*\.ad(force|runner|se?rve?|stream|\d*|view|s|log|vert(s|enties|is(ing|e?ments)?)?)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.53"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'ad'</title>
  <title lang="en">Links with 'ad'</title>
  <description lang="de">Entferne frames/scripts mit 'ad' im Pfad.</description>
  <description lang="en">Remove frames/scripts with ad words in the path name.</description>
  <attr name="src">/(web)?ad(force|runner|se?rve?|stream|\d*|s|view|log|vert(s|enties|is(ing|e?ments)?)?)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.54"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'adbouncer'</title>
  <title lang="en">Links with 'adbouncer'</title>
  <description lang="de">Entferne frames/scripts mit 'adbouncer' im Pfad.</description>
  <description lang="en">Remove frames/scripts with 'adbouncer' in the path name.</description>
  <attr name="src">/adbouncer\.phtml</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.55"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'easy-cash'</title>
  <title lang="en">Links with 'easy-cash'</title>
  <description lang="de">Entferne frames/scripts mit 'easy-cash' im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'easy-cash' in the host name.</description>
  <attr name="src">easy-cash|/jsads/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.56"
 tag="iframe|script">
  <title lang="de">Onmouseover Werbung</title>
  <title lang="en">Onmouseover ads</title>
  <description lang="de">Entfernt JavaScript Werbung.</description>
  <description lang="en">Gets rid of JavaScript annoyances.</description>
  <attr name="onmouseover">parent\.location\s*=</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.57"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'ads'</title>
  <title lang="en">Links with 'ads'</title>
  <description lang="de">Entferne frames/scripts mit 'ads' im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'ads' in the host name.</description>
  <attr name="src">https?://(servedby\.)?ad(s|server(\d+)?|vertising)?\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.58"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'trade' u.a.</title>
  <title lang="en">Links with 'trade' etc.</title>
  <description lang="de">Entferne frames/scripts mit 'trade' und weiteren im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'trade' and others in the host name.</description>
  <attr name="src">https?://[^/]*(tradedoubler|emerchandise|ecommercetimes|ivwbox|sitemeter)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.59"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'linkexchange' u.a.</title>
  <title lang="en">Links with 'linkexchange' etc.</title>
  <description lang="de">Entferne frames/scripts mit 'linkexchange' und weiteren im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'linkexchange' and others in the host name.</description>
  <attr name="src">https?://[^/]*((link|media)exchange|mediaplex|realmedia|imgis|adsynergy|fast(click|counter|graphics)|hitexchange)\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.60"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'adclick'</title>
  <title lang="en">Links with 'adclick'</title>
  <description lang="de">Entferne frames/scripts mit 'adclick' im Pfad.</description>
  <description lang="en">Remove frames/scripts with 'adlink' in the path.</description>
  <attr name="src">/adclick\.(exe|php)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.61"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'banner' u.a.</title>
  <title lang="en">Links with 'banner' etc.</title>
  <description lang="de">Entferne frames/scripts mit 'banner' und weiteren im Pfad.</description>
  <description lang="en">Remove frames/scripts with 'banner' and others in the path.</description>
  <attr name="src">/(v?banner(s|_redirect|click)|clickit|werbung|RealMedia|phpAdsNew|adclick|AdServer)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.62"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'event.ng'</title>
  <title lang="en">Links with 'event.ng'</title>
  <description lang="de">Entferne frames/scripts mit 'event.ng' im Pfad.</description>
  <description lang="en">Remove frames/scripts with 'event.ng' in the path.</description>
  <attr name="src">/event\.ng(\?|/)Type=click</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.63"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'eu-adcenter'</title>
  <title lang="en">Links with 'eu-adcenter'</title>
  <description lang="de">Lösche frames/scripts mit 'eu-adcenter' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'eu-adcenter' in the path.</description>
  <attr name="src">\.eu-adcenter\.net</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.64"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'click'</title>
  <title lang="en">Links mit 'click'</title>
  <description lang="de">Remove frames/scripts with 'click' in the path.</description>
  <attr name="src">([\.\?]click[\?=]|click(stream|thrutraffic|thru|xchange)|clickId=|smartserve/click)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.65"
 tag="iframe|script">
  <title lang="de">frames/scripts mit 'werbung' u.a.</title>
  <title lang="en">Links with 'werbung' etc.</title>
  <description lang="de">Lösche frames/scripts mit 'werbung' und weiteren im Namen.</description>
  <description lang="en">Remove frames/scripts with 'werbung' and others in the path.</description>
  <attr name="src">/(publicite|werbung|rekla(ma|me|am)|annonse|maino(kset|nta|s)?)/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.66"
 tag="iframe|script">
  <title lang="de">frames/scripts zu Werberechnern 1</title>
  <title lang="en">Links to ad servers 1</title>
  <description lang="de">Entferne frames/scripts zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove frames/scripts to some ad servers.</description>
  <attr name="src">https?://((eur\.)?rd\.yahoo\.com|ar\.atwola\.com|partners\.webmasterplan\.com|www\.qksrv\.net|s0b\.bluestreak\.com|ar\.atwola\.com|pagead\.google\.com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.67"
 tag="iframe|script">
  <title lang="de">frames/scripts zu Werberechnern 2</title>
  <title lang="en">Links to ad servers 2</title>
  <description lang="de">Entferne frames/scripts zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove frames/scripts to some ad servers.</description>
  <attr name="src">(a\.tribalfusion\.com|ads\.adcode\.de|www\.bethedealer\.com|\.adbrite\.com|\.adengage\.com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.68"
 tag="iframe|script">
  <title lang="de">frames/scripts zu Werberechnern 3</title>
  <title lang="en">Links to ad servers 3</title>
  <description lang="de">Entferne frames/scripts zu verschiedenen Werberechnern.</description>
  <description lang="en">Remove frames/scripts to some ad servers.</description>
  <attr name="src">(adlink|microexchange|sponsornetz|spezialreporte|emedia|bannercommunity)\.de</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.69"
 tag="iframe|script">
  <title lang="de">Rechner mit 'click'</title>
  <title lang="en">Ad servers 10</title>
  <description lang="de">Blockiert Rechner mit 'click' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'click' words in the host name.</description>
  <attr name="src">https?://[^/]*(fastclick|doubleclick|click(it|finders|burst|here\.egroups))\.</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.70"
 tag="iframe|script">
  <title lang="de">CGI Werbung mit 'ads'</title>
  <title lang="en">CGI adverts with 'ads'</title>
  <description lang="de">Lösche frames/scripts mit 'ads' im CGI Namen.</description>
  <description lang="en">Remove frames/scripts with 'ads' in the CGI path.</description>
  <attr name="src">/cgi-bin/ads?(log(\.pl)?|click)?\?</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.71"
 tag="iframe|script">
  <title lang="de">CGI Werbung mit 'clickthru'</title>
  <title lang="en">CGI adverts with 'clickthru'</title>
  <description lang="de">Lösche frames/scripts mit 'clickthru' im CGI Namen.</description>
  <description lang="en">Remove frames/scripts with 'clickthru' in the CGI path.</description>
  <attr name="src">clickthru.(acc|aspx)\?</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.72"
 tag="iframe|script">
  <title lang="de">Entferne verknüpfungen mit 'doubleclick'</title>
  <title lang="en">Remove frames/scripts with 'doubleclick'</title>
  <description lang="de">Entferne frames/scripts mit 'doubleclick' im Rechnernamen.</description>
  <description lang="en">Remove frames/scripts with 'doubleclick' in the host name.</description>
  <attr name="src">(double|fast)click\.(net|com)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.73"
 tag="iframe|script">
  <title lang="de">Entferne frames/scripts mit 'buy_assets'</title>
  <title lang="en">Remove frames/scripts with 'buy_assets'</title>
  <description lang="de">Entferne frames/scripts mit 'buy_assets' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'buy_assets' in the name.</description>
  <attr name="src">/buy_assets/</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.74"
 tag="iframe|script">
  <title lang="de">Entferne frames/scripts mit 'value'</title>
  <title lang="en">Remove frames/scripts with 'value'</title>
  <description lang="de">Entferne frames/scripts mit 'value' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'value' in the name.</description>
  <attr name="src">value(stream|xchange|click)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.75"
 tag="iframe|script">
  <title lang="de">Entferne frames/scripts mit 'banner'</title>
  <title lang="en">Remove frames/scripts with 'banner'</title>
  <description lang="de">Entferne frames/scripts mit 'banner' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'banner' in the name.</description>
  <attr name="src">(top|bottom|left|right|)?banner(s|id=|\d|_)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.83"
 tag="iframe|script">
  <title lang="de">Entferne frames/scripts mit 'dime'</title>
  <title lang="en">Remove frames/scripts with 'dime'</title>
  <description lang="de">Entferne frames/scripts mit 'dime' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'dime' in the name.</description>
  <attr name="src">dime(xchange|click)|bidvertiser\.com</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.84"
 tag="iframe|script">
  <title lang="de">Entferne frames/scripts mit 'adlog'</title>
  <title lang="en">Remove frames/scripts with 'adlog'</title>
  <description lang="de">Entferne frames/scripts mit 'adlog' im Namen.</description>
  <description lang="en">Remove frames/scripts with 'adlog' in the name.</description>
  <attr name="src">adlog\.com\.|survey\.questionmarket\.com</attr>
  <replacement part="complete"/>
</htmlrewrite>
</folder>
