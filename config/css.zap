<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="CSS filtering"
 desc="Some browsers do not support CSS, so turn it off with these rules. Or you can test your pages without  CSS styles!  Well, we remove only complete &lt;style&gt; tags, not style=&quot;&quot; attributes. "
 disable="1">

<rewrite title="Remove STYLE tag"
 desc="Remove the &lt;style&gt; tag."
 tag="style">
</rewrite>
</folder>