<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="HTTP Headers"
 desc="Add, delete and modify HTTP headers.">

<header title="My own user-agent"
 desc="The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont. Some sites may not be displayed correctly with this option. A common User-Agent value could be &quot;Mozilla (compatible; MSIE 6.0b; Window NT 5.0)&quot;"
 name="User-Agent">Calzilla</header>

<header title="No Cookies"
 desc="Remove all set-cookie headers. Some sites may not work with this option because they require Cookies."
 disable="1"
 name="Set-Cookie"/>

<header title="No referer"
 desc="Remove the Referer header. Some sites may not work with this option, because they check the referer."
 disable="1"
 name="Referer"/>

<header title="No x-meta tags"
 desc="What the hell are x-meta tags? Definitely not something I need."
 name="x-meta"/>

<header title="No accepts"
 desc="This is really paranoid. Most browsers send Accept, Accept-Language, Accept-Encoding and Accept-Charset headers. These headers can reveal private information (eg. if you accept certain languages your ethnic group can be guessed).
"
 disable="1"
 name="Accept.*"/>
</folder>
