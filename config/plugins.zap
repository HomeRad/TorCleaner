<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Plugins" oid="1"
 desc="Some people must at all cost preserve bandwidth. The filter rules found here remove all plugin contents.">

<replacer title="Plugins with JavaScript" oid="0"
 desc="Some pages write HTML code with JavaScript. Use this with care, as it deletes the whole &lt;script&gt; block _and_ Python has a buggy re module, there occurs often inifinite recursion."
 disable="1"
 search="(?is)&lt;script.+?&lt;/(object|embed)&gt;.+?&lt;/script&gt;"/>

<rewrite title="Remove EMBEDded content" oid="1"
 desc="Kill &lt;embed&gt; things."
 tag="embed">
</rewrite>

<rewrite title="Remove OBJECTs" oid="2"
 desc="Kill &lt;object&gt; things."
 tag="object">
</rewrite>
</folder>
