<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Scripting" oid="4"
 desc="Scripting related.">

<rewrite title="&lt;a&gt; onfocus" oid="0"
 disable="1">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseout" oid="1"
 disable="1">
<attr name="onmouseout"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseover" oid="2"
 disable="1">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onfocus" oid="3"
 disable="1"
 tag="area">
<attr name="onfocus"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseout" oid="4"
 disable="1"
 tag="area">
<attr name="onmouseover"/>
<attr name="onmouseout"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseover" oid="5"
 disable="1"
 tag="area">
<attr name="onmouseover"/>
<replace part="attr"/>
</rewrite>

<rewrite title="[rewrite] &lt;body&gt; onload" oid="6"
 desc="Remove onload javascript attribute"
 disable="1"
 tag="body">
<attr name="onload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onresize" oid="7"
 desc="filter the onresize tag"
 tag="body">
<attr name="onresize"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onunload" oid="8"
 desc="onunload is used for advert popups "
 tag="body">
<attr name="onunload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;noscript&gt;" oid="9"
 desc="Remove &lt;noscript&gt; tag (use if you allowed scripting)"
 tag="noscript">
</rewrite>

<rewrite title="&lt;script&gt;" oid="10"
 desc="remove script tag (use if you dont want javascript)"
 disable="1"
 tag="script">
</rewrite>

<rewrite title="Javascript links" oid="11"
 disable="1">
<attr>javascript:.*</attr>
</rewrite>

<rewrite title="use contents of noscript tag" oid="12"
 desc="use if you are filtering script tags. This rule just removes the &lt;noscript&gt; tags, not the tag content."
 disable="1"
 tag="noscript">
<replace part="tag"/>
</rewrite>

<replacer title="top frame bashing" oid="13"
 desc="Some sites disable surrounding frames and install themselves as the top frame."
 search="top\.location\.href\s*=\s*self\.location\.href"/>

<javascript title="Enable JavaScript" oid="14"
 desc="The HTML parser will parse and execute Javascript to remove Popups, and delete JS advertising text written with document.write()"/>

<rewrite title="&lt;frameset&gt; onunload" oid="15"
 desc="onunload is used for advert popups"
 tag="frameset">
<attr name="onunload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;frame&gt; onunload" oid="16"
 desc="onunload is used for advert popups"
 tag="frame">
<attr name="onunload"/>
<replace part="attr"/>
</rewrite>

<rewrite title="Prevent right-click disablement" oid="17"
 desc="Good! Adaptation, improvisation, but your weakness is not your technique."
 tag="script">
<enclosed>(?i)document\.onmousedown</enclosed>
</rewrite>

<rewrite title="&lt;body&gt; ondragstart" oid="18"
 tag="body">
<attr name="ondragstart"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; oncontextmenu" oid="19"
 tag="body">
<attr name="oncontextmenu"/>
<replace part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onselectstart" oid="20"
 tag="body">
<attr name="onselectstart"/>
<replace part="attr"/>
</rewrite>
</folder>
