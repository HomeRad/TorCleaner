<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.366" oid="5" configversion="0.10">
<title lang="de">Zähler und Statistik</title>
<title lang="en">Trackers and counters</title>
<description lang="en">Statistic links and tracker images deserve now a separate category as they became a lot more in the last couple of months.</description>

<block sid="wc.363"
 url="https?://(nedstatbasic\.net|nedstat\.nl|ivwbox\.de|stats\.esomniture\.com)">
  <title lang="de">Statistik Seiten</title>
  <title lang="en">Statistic sites</title>
  <description lang="de">Einige Statistik-Seiten.</description>
  <description lang="en">Some tracker sites</description>
</block>

<htmlrewrite sid="wc.6"
 tag="a">
  <title lang="de">Statistik Seiten 2</title>
  <title lang="en">Statistic sites 2</title>
  <attr name="href">^https?://[0-9a-z.]*(nedstatbasic\.net|nedstat\.nl|ivwbox\.de)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.364"
 tag="img">
  <title lang="de">1x1 Zählerbilder</title>
  <title lang="en">1x1 tracker images</title>
  <description lang="de">Einige Seiten benutzen 1x1 Bilder um Benutzer zu zählen.</description>
  <description lang="en">Several sites use 1x1 images to track users.</description>
  <attr name="width">^1$</attr>
  <attr name="height">^1$</attr>
  <replacement part="complete"/>
</htmlrewrite>

<image sid="wc.365"
 width="1"
 height="1">
  <title lang="de">1x1 Zählerbilder 2</title>
  <title lang="en">1x1 tracker images 2</title>
  <description lang="de">Für den Fall dass width und height Attribute fehlen.</description>
  <description lang="en">In case the width and height attributes are missing</description>
</image>

<htmlrewrite sid="wc.25"
 tag="img">
  <title lang="de">0x0 Zählerbilder</title>
  <title lang="en">0x0 tracker images</title>
  <description lang="de">Einige Seiten benutzen 0x0 Bilder um Benutzer zu zählen.</description>
  <description lang="en">Several sites use 0x0 images to track users.</description>
  <attr name="width">^0$</attr>
  <attr name="height">^0$</attr>
  <replacement part="complete"/>
</htmlrewrite>

<image sid="wc.5">
  <title lang="de">0x0 Zählerbilder 2</title>
  <title lang="en">0x0 tracker images 2</title>
  <description lang="de">Für den Fall dass width und height Attribute fehlen.</description>
  <description lang="en">In case the width and height attributes are missing</description>
</image>

<block sid="wc.1"
 url="siemens\.com/tracking_engine/StatServ">
  <title lang="en">Siemens StatServ</title>
</block>

<htmlrewrite sid="wc.21"
 tag="a">
  <title lang="de">Verschiedene Zählskripte</title>
  <title lang="en">Counter scripts</title>
  <description lang="de">CGI Skripte zur Zählung</description>
  <description lang="en">CGI scripts counting web hits</description>
  <attr name="href">/(count|track)(er|run)?\.(pl|cgi|exe|dll|asp|php[34]?)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.93"
 tag="a">
  <title lang="de">Verschiedene Zählskripte 2</title>
  <title lang="en">Counter scripts 2</title>
  <description lang="de">CGI Skripte zur Zählung</description>
  <description lang="en">CGI scripts counting web hits</description>
  <attr name="href">cqcounter\.com</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.406"
 tag="img">
  <title lang="de">akamai.net Statistik</title>
  <title lang="en">SF tracker image</title>
  <description lang="de">Zu finden auf Sourceforge.</description>
  <description lang="en">akamai tracker image at sourceforge</description>
  <attr name="src">e\.akamai\.net</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.94"
 tag="script">
  <title lang="de">alexa.com Statistik</title>
  <title lang="en">alexa.com statistics</title>
  <attr name="src">xslt\.alexa\.com/site_stats</attr>
  <replacement part="complete"/>
</htmlrewrite>
</folder>
