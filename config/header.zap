<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.323" title="HTTP Headers"
 desc="Add, delete and modify HTTP headers." oid="2">
<header sid="wc.313" title="My own user-agent"
 desc="The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option (mail them to me and I add them to the dont match url). A common User-Agent value could be &amp;quot;Mozilla (compatible; MSIE 6.0b; Window NT 5.0)&amp;quot;"
 name="User-Agent" value="Calzilla/6.0"/>

<header sid="wc.314" title="No referer"
 desc="Remove the Referer header. Some sites may not work with this option, because they check the referer. In this case add them to &apos;dont match url&apos; and write me an email."
 name="Referer">
<nomatchurl>printerfriendly\.abcnews\.com</nomatchurl>
<nomatchurl>/cgi-bin/fosi\.cgi</nomatchurl>
<nomatchurl>\.ask\.com</nomatchurl>
<nomatchurl>www\.amazon\.de/exec/obidos/clipserve/</nomatchurl>
<nomatchurl>\.lufthansa\.</nomatchurl>
<nomatchurl>www\.nba\.com</nomatchurl>
</header>

<header sid="wc.315" title="No x-meta tags"
 desc="What the hell are x-meta tags? Definitely not something I need."
 name="X-Meta"/>

<header sid="wc.316" title="No via"
 desc="Proxies (including WebCleaner) add a &apos;Via&apos; header in the outgoing request. This rule prevents this."
 name="Via"/>

<header sid="wc.317" title="No accepts"
 desc="This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages your ethnic group can be guessed). This rule is disabled per default because I use the Accept-Language headers. "
 disable="1"
 name="Accept.*"/>

<header sid="wc.318" title="No X-Forwarded-For"
 desc="This header is used by many proxy servers (e.g., Squid) to note whom a request has been forwarded for"
 name="X-Forwarded-For"/>

<header sid="wc.319" title="No From"
 desc="Enhance privacy by removing the from: header."
 name="From$"/>

<header sid="wc.320" title="No Client-ip"
 desc="The Client-ip header is an extension header used by some older clients and some proxies to transmit the IP address of the machine on which the client is running."
 name="Client-ip"/>

<header sid="wc.321" title="No UA-*"
 desc="These User-Agent headers are nonstandard and no longer common. They provide information about the client machine that could allow for better content selection by a server. For instance, if a server knew that a user&apos;s machine had only an 8-bit color display, the server could select images that were optimized for that type of display."
 name="UA-.*"/>

<header sid="wc.322" title="No Cookies"
 desc="Remove all set-cookie headers. Some sites may not work with this option because they require Cookies. This rule is disabled per default because I use the browser&apos;s Cookie management interface: everytime someone wants to set a cookie the browser displays a question if I want to set it."
 disable="1"
 name="Set-Cookie"/>
</folder>
