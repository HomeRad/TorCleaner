<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="HTTP Headers" oid="6"
 desc="Add, delete and modify HTTP headers.">

<header title="My own user-agent" oid="0"
 desc="The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option. A common User-Agent value could be &amp;quot;Mozilla (compatible; MSIE 6.0b; Window NT 5.0)&amp;quot;"
 name="User-Agent">Calzilla</header>

<header title="No Cookies" oid="1"
 desc="Remove all set-cookie headers. Some sites may not work with this option because they require Cookies."
 disable="1"
 name="Set-Cookie"/>

<header title="No accepts" oid="2"
 desc="This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages your ethnic group can be guessed). "
 disable="1"
 name="Accept.*"/>

<header title="No referer" oid="3"
 desc="Remove the Referer header. Some sites may not work with this option, because they check the referer. In this case add them to &apos;dont match url&apos; and write me an email."
 name="Referer"/>

<header title="No x-meta tags" oid="4"
 desc="What the hell are x-meta tags? Definitely not something I need."
 name="x-meta"/>

<header title="No via" oid="5"
 desc="Proxies (including WebCleaner) add a &apos;Via&apos; header in the outgoing request. This rule prevents this."
 name="via"/>

<header title="No X-Forwarded-For" oid="6"
 name="X-Forwarded-For"/>
</folder>
