<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.381" oid="6" title="Miscellaneous"
 desc="Misc things we dont like in our HTML source :)">

<rewrite sid="wc.367" oid="0" title="No meta tags 1"
 desc="Meta tags with name attribute are only for search engines."
 tag="meta">
<attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.368" oid="1" title="Remove IE shortcut icon"
 desc="Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this."
 tag="link">
<attr name="rel">(?i)shortcut icon</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.369" oid="2" title="Remove IFRAMEs"
 desc="&lt;iframe&gt; content is almost always advertising. So remove it."
 dontmatchurl="www\.eselfilme\.de"
 tag="iframe"/>


<rewrite sid="wc.370" oid="3" title="Remove NOFRAMES"
 desc="Most of the browsers have frames so they dont need the &lt;noframes&gt; content."
 tag="noframes"/>


<nocomments sid="wc.371" oid="4" title="Remove all HTML comments"
 dontmatchurl="(oreillynet.com|www.onlamp.com|www.onjava.com)"/>

<rewrite sid="wc.372" oid="5" title="Replace BLINK with B"
 desc="Dont we all hate the &lt;blink&gt; tag?"
 tag="blink">
<replacement part="tagname">b</replacement>
</rewrite>

<replace sid="wc.373" oid="6" title="Replace blink CSS"
 desc="Unfuckingbelievable they made a blink CSS entry."
 search="text-decoration:\s*blink"/>

<rewrite sid="wc.374" oid="7" title="Replace MARQUEE with SPAN"
 desc="Jeeesus, as if blinking isn&apos;t enough."
 tag="marquee">
<replacement part="tagname">span</replacement>
</rewrite>

<replace sid="wc.375" oid="8" title="Love and Peace"
 desc="Love &amp; Peace!"
 search="(US-Präsident|George( W.)?) Bush"/>

<rewrite sid="wc.376" oid="9" title="Remove LOWSRC"
 desc="The lowsrc is waste of bandwidth if you have enough of it ;)"
 tag="img">
<attr name="lowsrc"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.377" oid="10" title="Remove _blank and _new targets"
 desc="Can&apos;t believe I have to make this case-insensitive 8-)">
<attr name="target">(?i)_(blank|new)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.378" oid="11" title="Remove _blank and _new area targets"
 tag="area">
<attr name="target">(?i)_(blank|new)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.379" oid="12" title="Eselfilme layer"
 matchurl="eselfilme.de"
 tag="div">
<attr name="id">Layer1</attr>
<replacement part="complete"/>
</rewrite>

<replace sid="wc.380" oid="13" title="The Dude"
 desc="Just a silly example."
 disable="1"
 search="Bastian"/>
</folder>
