<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Scripting"
 desc="No scripting. Scripting steenks! Yes.">

<rewrite title="&lt;a&gt; onfocus">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseout">
<attr name="onmouseout"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseover">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onfocus"
 tag="area">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseout"
 tag="area">
<attr name="onmouseout"/>
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseover"
 tag="area">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onload"
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
 tag="body">
<attr name="onunload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;noscript&gt; OFF"
 desc="Remove &lt;noscript&gt; contents."
 disable="1"
 tag="noscript">
</rewrite>

<rewrite title="&lt;noscript&gt; ON"
 tag="noscript">
<replace part="tag"/>
</rewrite>

<rewrite title="&lt;script&gt; OFF"
 tag="script">
</rewrite>

<rewrite title="Javascript links">
<attr>javascript:.*</attr>
</rewrite>
</folder>