<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Plugins" oid="2"
 desc="The filter rules found here remove plugin (eg flash) contents, but only for selected sites.">

<rewrite title="Remove EMBEDded content" oid="0"
 desc="Kill &lt;embed&gt; things."
 matchurl="www\.heise\.de"
 tag="embed"/>


<rewrite title="Remove OBJECTs" oid="1"
 desc="Kill &lt;object&gt; things."
 matchurl="www\.heise\.de"
 tag="object"/>

</folder>
