<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.289" title="Plugins"
 desc="The filter rules found here remove plugin (eg flash) contents, but only for selected sites." oid="3">
<rewrite sid="wc.287" title="Remove EMBEDded content"
 desc="Kill &lt;embed&gt; things."
 tag="embed">
<matchurl>www\.heise\.de</matchurl>
</rewrite>


<rewrite sid="wc.288" title="Remove OBJECTs"
 desc="Kill &lt;object&gt; things."
 tag="object">
<matchurl>www\.heise\.de</matchurl>
</rewrite>

</folder>
