<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="CSS filtering" oid="14"
 desc="Some browsers do not support CSS, so turn it off with these rules. Or you can test your pages without  CSS styles!  Well, we remove only complete &lt;style&gt; tags, not style=&amp;quot;&amp;quot; attributes. "
 disable="1">

<rewrite title="Remove STYLE tag" oid="0"
 desc="Remove the &lt;style&gt; tag."
 tag="style"/>

</folder>
