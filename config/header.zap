<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="HTTP Headers"
 desc="Add, delete and modify HTTP headers.">

<header title="My own user-agent"
 desc="The user-agent is the most widely used HTTP header to detect your browser. Some people might like it, some dont. I dont."
 name="User-Agent">Calzilla</header>

<header title="No x-meta tags"
 desc="What the hell are x-meta tag? Definitely not something I need."
 disable="1"
 name="x-meta"/>

<header title="No referer"
 desc="Remove the Referer header"
 name="Referer"/>
</folder>