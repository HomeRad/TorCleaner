<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.312" title="Scripting"
 desc="Scripting related." oid="4">
<javascript sid="wc.304" title="Enable JavaScript engine"
 desc="The HTML parser will parse and execute Javascript to remove Popups, and delete JS advertising text written with document.write()"
 dontmatchurl="(msdn\.microsoft\.com|www\.mvhs\.de)"/>

<rewrite sid="wc.290" title="&lt;a&gt; onfocus">
<attr name="onfocus"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.291" title="&lt;a&gt; onmouseout">
<attr name="onmouseout"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.292" title="&lt;a&gt; onmouseover">
<attr name="onmouseover"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.293" title="&lt;area&gt; onfocus"
 tag="area">
<attr name="onfocus"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.294" title="&lt;area&gt; onmouseout"
 tag="area">
<attr name="onmouseover"/>
<attr name="onmouseout"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.295" title="&lt;area&gt; onmouseover"
 tag="area">
<attr name="onmouseover"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.296" title="&lt;body&gt; onload"
 desc="Remove onload javascript attribute"
 disable="1"
 tag="body">
<attr name="onload"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.297" title="&lt;body&gt; onresize"
 desc="filter the onresize tag"
 tag="body">
<attr name="onresize"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.298" title="&lt;body&gt; onunload"
 desc="onunload is used for advert popups "
 tag="body">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.299" title="&lt;noscript&gt;"
 desc="Remove &lt;noscript&gt; tag (use if you allowed scripting)"
 tag="noscript"/>


<rewrite sid="wc.300" title="Disable Javascript"
 desc="Remove Javascript for certain pages."
 matchurl="apnews\.excite\.com"
 tag="script"/>


<rewrite sid="wc.301" title="Remove Javascript links"
 desc="Only activate this rule if Javascript is disabled in your browser."
 disable="1">
<attr>javascript:.*</attr>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.302" title="Use noscript tag"
 desc="Only activate this rule if Javascript is disabled in your browser."
 disable="1"
 tag="noscript">
<replacement part="tag"/>
</rewrite>

<replace sid="wc.303" title="Disable top frame bashing"
 desc="Some sites disable surrounding frames and install themselves as the top frame."
 search="top\.location\.href\s*=\s*self\.location\.href"/>

<rewrite sid="wc.305" title="&lt;frameset&gt; onunload"
 desc="onunload is used for advert popups"
 tag="frameset">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.306" title="&lt;frame&gt; onunload"
 desc="onunload is used for advert popups"
 tag="frame">
<attr name="onunload"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.307" title="Prevent right-click disablement"
 desc="Good! Adaptation, improvisation, but your weakness is not your technique."
 tag="script">
<enclosed>(?i)document\.onmousedown</enclosed>
<replacement part="complete"/>
</rewrite>

<rewrite sid="wc.308" title="&lt;body&gt; ondragstart"
 tag="body">
<attr name="ondragstart"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.309" title="&lt;body&gt; oncontextmenu"
 tag="body">
<attr name="oncontextmenu"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.310" title="&lt;body&gt; onselectstart"
 tag="body">
<attr name="onselectstart"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.311" title="&lt;body&gt; onkeydown"
 tag="body">
<attr name="onkeydown"/>
<replacement part="attr"/>
</rewrite>
</folder>
