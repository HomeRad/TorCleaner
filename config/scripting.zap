<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Scripting" oid="4"
 desc="Scripting related.">

<rewrite title="&lt;a&gt; onfocus" oid="0">
<attr name="onfocus"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseout" oid="1">
<attr name="onmouseout"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;a&gt; onmouseover" oid="2">
<attr name="onmouseover"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onfocus" oid="3"
 tag="area">
<attr name="onfocus"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseout" oid="4"
 tag="area">
<attr name="onmouseover"/>
<attr name="onmouseout"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;area&gt; onmouseover" oid="5"
 tag="area">
<attr name="onmouseover"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onload" oid="6"
 desc="Remove onload javascript attribute"
 disable="1"
 tag="body">
<attr name="onload"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onresize" oid="7"
 desc="filter the onresize tag"
 tag="body">
<attr name="onresize"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onunload" oid="8"
 desc="onunload is used for advert popups "
 tag="body">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;noscript&gt;" oid="9"
 desc="Remove &lt;noscript&gt; tag (use if you allowed scripting)"
 tag="noscript"/>


<rewrite title="&lt;script&gt;" oid="10"
 desc="Only activate this rule if Javascript is disabled in your browser."
 disable="1"
 tag="script"/>


<rewrite title="Javascript links" oid="11"
 desc="Only activate this rule if Javascript is disabled in your browser."
 disable="1">
<attr>javascript:.*</attr>
</rewrite>

<rewrite title="use contents of noscript tag" oid="12"
 desc="Only activate this rule if Javascript is disabled in your browser."
 disable="1"
 tag="noscript">
<replacement part="tag"/>
</rewrite>

<replace title="top frame bashing" oid="13"
 desc="Some sites disable surrounding frames and install themselves as the top frame."
 search="top\.location\.href\s*=\s*self\.location\.href"/>

<javascript title="Enable JavaScript engine" oid="14"
 desc="The HTML parser will parse and execute Javascript to remove Popups, and delete JS advertising text written with document.write()"/>

<rewrite title="&lt;frameset&gt; onunload" oid="15"
 desc="onunload is used for advert popups"
 tag="frameset">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;frame&gt; onunload" oid="16"
 desc="onunload is used for advert popups"
 tag="frame">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="Prevent right-click disablement" oid="17"
 desc="Good! Adaptation, improvisation, but your weakness is not your technique."
 tag="script">
<enclosed>(?i)document\.onmousedown</enclosed>
</rewrite>

<rewrite title="&lt;body&gt; ondragstart" oid="18"
 tag="body">
<attr name="ondragstart"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; oncontextmenu" oid="19"
 tag="body">
<attr name="oncontextmenu"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onselectstart" oid="20"
 tag="body">
<attr name="onselectstart"/>
<replacement part="attr"/>
</rewrite>

<rewrite title="&lt;body&gt; onkeydown" oid="21"
 tag="body">
<attr name="onkeydown"/>
<replacement part="attr"/>
</rewrite>
</folder>
