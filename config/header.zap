<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="HTTP Headers" oid="2"
 desc="Add, delete and modify HTTP headers.">

<header title="My own user-agent" oid="0"
 desc="The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option (mail them to me and I add them to the dont match url). A common User-Agent value could be &amp;quot;Mozilla (compatible; MSIE 6.0b; Window NT 5.0)&amp;quot;"
 name="User-Agent">Calzilla/6.0</header>

<header title="No Cookies" oid="1"
 desc="Remove all set-cookie headers. Some sites may not work with this option because they require Cookies. This rule is disabled per default because I use the browser&apos;s Cookie management interface: everytime someone wants to set a cookie the browser displays a question if I want to set it."
 disable="1"
 name="Set-Cookie"/>

<header title="No accepts" oid="2"
 desc="This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages your ethnic group can be guessed). This rule is disabled per default because I use the Accept-Language headers. "
 disable="1"
 name="Accept.*"/>

<header title="No referer" oid="3"
 desc="Remove the Referer header. Some sites may not work with this option, because they check the referer. In this case add them to &apos;dont match url&apos; and write me an email."
 dontmatchurl="(printerfriendly\.abcnews\.com|/cgi-bin/fosi\.cgi|\.ask\.com|www\.amazon\.de/exec/obidos/clipserve/|\.lufthansa\.|www\.nba\.com)"
 name="Referer"/>

<header title="No x-meta tags" oid="4"
 desc="What the hell are x-meta tags? Definitely not something I need."
 name="X-Meta"/>

<header title="No via" oid="5"
 desc="Proxies (including WebCleaner) add a &apos;Via&apos; header in the outgoing request. This rule prevents this."
 name="Via"/>

<header title="No X-Forwarded-For" oid="6"
 desc="This header is used by many proxy servers (e.g., Squid) to note whom a request has been forwarded for"
 name="X-Forwarded-For"/>

<header title="No From" oid="7"
 desc="Enhance privacy by removing the from: header."
 name="From$"/>

<header title="No Client-ip" oid="8"
 desc="The Client-ip header is an extension header used by some older clients and some proxies to transmit the IP address of the machine on which the client is running."
 name="Client-ip"/>

<header title="No UA-*" oid="9"
 desc="These User-Agent headers are nonstandard and no longer common. They provide information about the client machine that could allow for better content selection by a server. For instance, if a server knew that a user&apos;s machine had only an 8-bit color display, the server could select images that were optimized for that type of display."
 name="UA-.*"/>
</folder>
