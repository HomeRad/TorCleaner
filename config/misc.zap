<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.381" title="Miscellaneous"
 desc="Misc things we dont like in our HTML source :)" oid="6">
<rewrite sid="wc.367" title="No meta tags 1"
 desc="Meta tags with name attribute are only for search engines."
 tag="meta">
<attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.368" title="Remove IE shortcut icon"
 desc="Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this."
 tag="link">
<attr name="rel">(?i)shortcut icon</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.369" title="Remove IFRAMEs"
 desc="&lt;iframe&gt; content is almost always advertising. So remove it."
 dontmatchurl="(www\.eselfilme\.de|coverviewer\.sourceforge\.net)"
 tag="iframe"/>


<rewrite sid="wc.370" title="Remove NOFRAMES"
 desc="Most of the browsers have frames so they dont need the &lt;noframes&gt; content."
 tag="noframes"/>


<nocomments sid="wc.371" title="Remove all HTML comments"
 dontmatchurl="(oreillynet.com|www.onlamp.com|www.onjava.com)"/>

<rewrite sid="wc.372" title="Replace BLINK with B"
 desc="Dont we all hate the &lt;blink&gt; tag?"
 tag="blink">
<replacement part="tagname">b</replacement>
</rewrite>

<replace sid="wc.373" title="Replace blink CSS"
 desc="Unfuckingbelievable they made a blink CSS entry."
 search="text-decoration:\s*blink"/>

<rewrite sid="wc.374" title="Replace MARQUEE with SPAN"
 desc="Jeeesus, as if blinking isn&apos;t enough."
 tag="marquee">
<replacement part="tagname">span</replacement>
</rewrite>

<replace sid="wc.375" title="Love and Peace"
 desc="Love &amp; Peace!"
 search="(US-Präsident|George( W.)?) Bush"/>

<rewrite sid="wc.376" title="Remove LOWSRC"
 desc="The lowsrc is waste of bandwidth if you have enough of it ;)"
 tag="img">
<attr name="lowsrc"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.377" title="Remove dumb href targets"
 desc="Can&apos;t believe I have to make this case-insensitive 8-)">
<attr name="target">(?i)_(blank|new|top)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.378" title="Remove dumb area targets"
 tag="area">
<attr name="target">(?i)_(blank|new)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.3" title="Mark href targets"
 desc="Display a little marker when links point to unknown targets.">
<attr name="target">(?i)^(?!_parent)(.+)$</attr>
<replacement part="attr">target=\1 style=cursor:ne-resize</replacement>
</rewrite>

<rewrite sid="wc.379" title="Eselfilme layer"
 matchurl="eselfilme.de"
 tag="div">
<attr name="id">Layer1</attr>
<replacement part="complete"/>
</rewrite>

<replace sid="wc.380" title="The Dude"
 desc="Just a silly example."
 disable="1"
 search="Bastian">The Dude</replace>
</folder>
