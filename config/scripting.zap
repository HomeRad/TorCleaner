<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Scripting"
 desc="Scripting related.">

<rewrite title="&lt;a&gt; onfocus"
 disable="1">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseout"
 disable="1">
<attr name="onmouseout"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseover"
 disable="1">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onfocus"
 disable="1"
 tag="area">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseout"
 disable="1"
 tag="area">
<attr name="onmouseout"/>
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseover"
 disable="1"
 tag="area">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onload"
 disable="1"
 tag="body">
<attr name="onload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onresize"
 desc="filter the onresize tag"
 tag="body">
<attr name="onresize"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onunload"
 desc="unonload is almost always used for advert popups "
 tag="body">
<attr name="onunload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="Javascript links"
 disable="1">
<attr>javascript:.*</attr>
</rewrite>

<rewrite title="&lt;noscript&gt;"
 desc="Remove &lt;noscript&gt; tag (use if you allowed scripting)"
 tag="noscript">
</rewrite>

<rewrite title="&lt;script&gt;"
 desc="remove script tag (use if you dont want javascript)"
 disable="1"
 tag="script">
</rewrite>

<rewrite title="use contents of noscript tag"
 desc="use if you are filtering script tags. This rule
just removes the &lt;noscript&gt; tags, not the
tag content."
 disable="1"
 tag="noscript">
<replace part="tag"/>
</rewrite>
</folder>