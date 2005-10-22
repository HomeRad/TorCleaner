<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.323" oid="6" configversion="0.10">
<title lang="de">HTTP Kopfdaten</title>
<title lang="en">HTTP Headers</title>
<description lang="en">Add, delete and modify HTTP headers.</description>

<header sid="wc.313"
 name="User-Agent"
 filterstage="request"
 action="replace">
  <title lang="de">Ersetze 'User-Agent'</title>
  <title lang="en">Replace 'User-Agent'</title>
  <description lang="de">Der user-agent ist das am meisten benutzte HTTP Kopfdatum zur Browserunterscheidung. Einige Seiten werden nicht richtig dargestellt wenn der falsche Browser erkannt wird.</description>
  <description lang="en">The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option (mail them to me and I add them to the dont match url). A common User-Agent value could be "Mozilla (compatible; MSIE 6.0b; Window NT 5.0)"</description>
  <nomatchurl>www\.k3b\.org</nomatchurl>
  <nomatchurl>www\.microsoft\.com</nomatchurl>
  <replacement>Calzilla/6.0</replacement>
</header>

<header sid="wc.314"
 name="Referer"
 filterstage="request"
 action="replace">
  <title lang="de">Ersetze 'Referer'</title>
  <title lang="en">Replace 'Referer'</title>
  <description lang="de">Ersetze das Referer Kopfdatum. Einige Seiten funktionieren mit dieser Einstellung nicht.</description>
  <description lang="en">Replace the Referer header. Some sites may not work with this option, because they check the referer. In this case add them to "Don't match URL" list and write me an email.</description>
  <replacement>http://$host/</replacement>
</header>

<header sid="wc.316"
 name="Via"
 filterstage="both"
 action="remove">
  <title lang="de">Entferne 'Via'</title>
  <title lang="en">Remove 'Via'</title>
  <description lang="de">Proxies (inklusive WebCleaner) fügen das 'Via' Kopfdatum zu einer ausgehenden Anfrage hinzu. Diese Regel verhindert dies.</description>
  <description lang="en">Proxies (including WebCleaner) add a 'Via' header in the outgoing request. This rule prevents this.</description>
</header>

<header sid="wc.317" disable="1"
 name="Accept.*"
 filterstage="request"
 action="remove">
  <title lang="de">Entferne 'Accept*'</title>
  <title lang="en">Remove 'Accepts*'</title>
  <description lang="de">Dies ist paranoid. Die meisten Browser senden Accept, Accept-Language, Accept-Encoding und Accept-Charset Kopfdaten. 
Diese Daten können private Informationen enthalten (z.B.wenn Sie bestimmte Sprachen akzeptieren). Diese Regel ist standardmäßig deaktiviert weil ich die Accept-Language Kopfdaten benutze.</description>
  <description lang="en">This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages). This rule is disabled per default because I use the Accept-Language headers.</description>
</header>

<header sid="wc.318"
 name="^X-(Forwarded-For|Junk|N|meta)$"
 filterstage="both"
 action="remove">
  <title lang="de">Entferne 'X-Forwared-For'</title>
  <title lang="en">Remove 'X-&lt;something&gt;'</title>
  <description lang="de">Dieses Kopfdatum wird von vielen Proxy Servern (z.B. Squid) benutzt, um zu notieren, für wen eine Anfrage weitergeleitet wurde.</description>
  <description lang="en">Remove unused X-&lt;something&gt; headers.</description>
</header>

<header sid="wc.319"
 name="From$"
 filterstage="request"
 action="remove">
  <title lang="de">Entferene 'From'</title>
  <title lang="en">Remove 'From'</title>
  <description lang="de">Entferne das From Kopfdatum, welches ansonsten den Absender einer Anfrage enthält.</description>
  <description lang="en">Enhance privacy by removing the from: header.</description>
</header>

<header sid="wc.321"
 name="UA-.*"
 filterstage="request"
 action="remove">
  <title lang="de">Entferne 'UA-*'</title>
  <title lang="en">Remove 'UA-*'</title>
  <description lang="de">Diese User-Agent Kopfdaten sind unüblich und veraltet. Sie enthalten Informationen über den Rechner des Benutzers.</description>
  <description lang="en">These User-Agent headers are nonstandard and no longer common. They provide information about the client machine.</description>
</header>

<header sid="wc.320"
 name="Client-ip"
 filterstage="request"
 action="remove">
  <title lang="de">Entferne 'Client-Ip'</title>
  <title lang="en">Remove 'Client-Ip'</title>
  <description lang="de">Das Client-ip Kopfdatum enthält die Rechnernummer des Benutzers.</description>
  <description lang="en">The Client-ip header transmits the IP address of the machine on which the client is running.</description>
</header>

<header sid="wc.322" disable="1"
 name="Set-Cookie"
 filterstage="both"
 action="remove">
  <title lang="de">Entferne Cookies</title>
  <title lang="en">Remove cookies</title>
  <description lang="de">Entferne Alle 'Set-Cookie' Kopfdaten. Einige Seiten funktionieren ohne Cookies nicht. Diese Regel ist standardmäßig deaktiviert.</description>
  <description lang="en">Remove all set-cookie headers. Some sites may not work with this option because they require cookies. This rule is disabled per default.</description>
</header>
</folder>
