<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.323" oid="2">
<title lang="en">HTTP Headers</title>
<description lang="en">Add, delete and modify HTTP headers.</description>
<header sid="wc.313"
 name="User-Agent">
<title lang="en">My own user-agent</title>
<description lang="en">The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option (mail them to me and I add them to the dont match url). A common User-Agent value could be &amp;quot;Mozilla (compatible; MSIE 6.0b; Window NT 5.0)&amp;quot;</description>
<replacement>Calzilla/6.0</replacement>
</header>

<header sid="wc.314"
 name="Referer">
<title lang="en">No referer</title>
<description lang="en">Remove the Referer header. Some sites may not work with this option, because they check the referer. In this case add them to &apos;dont match url&apos; and write me an email.</description>
<nomatchurl>printerfriendly\.abcnews\.com</nomatchurl>
<nomatchurl>/cgi-bin/fosi\.cgi</nomatchurl>
<nomatchurl>\.ask\.com</nomatchurl>
<nomatchurl>www\.amazon\.de/exec/obidos/clipserve/</nomatchurl>
<nomatchurl>\.lufthansa\.</nomatchurl>
<nomatchurl>www\.nba\.com</nomatchurl>
</header>

<header sid="wc.315"
 name="X-Meta">
<title lang="en">No x-meta tags</title>
<description lang="en">What the hell are x-meta tags? Definitely not something I need.</description>
</header>

<header sid="wc.316"
 name="Via">
<title lang="en">No via</title>
<description lang="en">Proxies (including WebCleaner) add a &apos;Via&apos; header in the outgoing request. This rule prevents this.</description>
</header>

<header sid="wc.317"
 disable="1"
 name="Accept.*">
<title lang="en">No accepts</title>
<description lang="en">This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages your ethnic group can be guessed). This rule is disabled per default because I use the Accept-Language headers.</description>
</header>

<header sid="wc.318"
 name="X-Forwarded-For">
<title lang="en">Enhance privacy by removing the from: header.</title>
<description lang="en">This header is used by many proxy servers (e.g., Squid) to note whom a request has been forwarded for</description>
</header>

<header sid="wc.319"
 name="From$">
<title lang="en">No From</title>
<description lang="en">Enhance privacy by removing the from: header.</description>
</header>

<header sid="wc.320"
 name="Client-ip">
<title lang="en">No Client-ip</title>
<description lang="en">The Client-ip header is an extension header used by some older clients and some proxies to transmit the IP address of the machine on which the client is running.</description>
</header>

<header sid="wc.321"
 name="UA-.*">
<title lang="en">No UA-*</title>
<description lang="en">These User-Agent headers are nonstandard and no longer common. They provide information about the client machine that could allow for better content selection by a server. For instance, if a server knew that a user&apos;s machine had only an 8-bit color display, the server could select images that were optimized for that type of display.</description>
</header>

<header sid="wc.322"
 disable="1"
 name="Set-Cookie">
<title lang="en">No Cookies</title>
<description lang="en">Remove all set-cookie headers. Some sites may not work with this option because they require Cookies. This rule is disabled per default because I use the browser&apos;s Cookie management interface: everytime someone wants to set a cookie the browser displays a question if I want to set it.</description>
</header>
</folder>
