<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Plugins" oid="1"
 desc="Some people must at all cost preserve bandwidth. The filter rules found here remove all plugin contents."
 disable="1">

<rewrite title="Remove EMBEDded content" oid="0"
 desc="Kill &lt;embed&gt; things."
 tag="embed">
</rewrite>

<rewrite title="Remove OBJECTs" oid="1"
 desc="Kill &lt;object&gt; things."
 tag="object">
</rewrite>
</folder>
