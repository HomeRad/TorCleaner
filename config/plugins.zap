<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.289" oid="3" title="Plugins"
 desc="The filter rules found here remove plugin (eg flash) contents, but only for selected sites.">

<rewrite sid="wc.287" oid="0" title="Remove EMBEDded content"
 desc="Kill &lt;embed&gt; things."
 matchurl="www\.heise\.de"
 tag="embed"/>


<rewrite sid="wc.288" oid="1" title="Remove OBJECTs"
 desc="Kill &lt;object&gt; things."
 matchurl="www\.heise\.de"
 tag="object"/>

</folder>
