<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Miscellaneous" oid="3"
 desc="Misc things we dont like in our HTML source :)">

<rewrite title="No meta tags 1" oid="0"
 desc="Meta tags with name attribute are only for search engines."
 tag="meta">
<attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
<replace part="tag"/>
</rewrite>

<rewrite title="Remove IE shortcut icon" oid="1"
 desc="Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this."
 tag="link">
<attr name="rel">(?i)shortcut icon</attr>
<replace part="tag"/>
</rewrite>

<rewrite title="Remove IFRAMEs" oid="2"
 desc="&lt;iframe&gt; content is almost always advertising. So remove it."
 dontmatchurl="www\.eselfilme\.de"
 tag="iframe">
</rewrite>

<rewrite title="Remove NOFRAMES" oid="3"
 desc="Most of the browsers have frames so they dont need the &lt;noframes&gt; content."
 tag="noframes">
</rewrite>

<nocomments title="Remove all HTML comments" oid="4"
 dontmatchurl="(oreillynet.com|www.onlamp.com|www.onjava.com)"/>

<rewrite title="Replace BLINK with B" oid="5"
 desc="Dont we all hate the &lt;blink&gt; tag?"
 tag="blink">
<replace part="tagname">b</replace>
</rewrite>

<replacer title="The Dude" oid="6"
 desc="Just a silly example."
 disable="1"
 search="Bastian">The Dude</replacer>

<replacer title="Replace blink CSS" oid="7"
 desc="Unfuckingbelievable they made a blink CSS entry."
 search="text-decoration:\s*blink">text-decoration: none</replacer>

<rewrite title="Replace MARQUEE with SPAN" oid="8"
 desc="Jeeesus, as if blinking isn&apos;t enough."
 tag="marquee">
<replace part="tagname">span</replace>
</rewrite>

<replacer title="Love and Peace" oid="9"
 desc="Love &amp; Peace!"
 search="(US-Präsident|George( W.)?) Bush">Love and Peace</replacer>

<replacer title="bllnk" oid="10"
 desc="&lt;blink&gt;&lt;/bllnk&gt; still does blink, so replace it. We might want to think later about correcting such typos automatically. For now it happens only at the india page. "
 matchurl="allindiaradio.org"
 search="&lt;/bllnk&gt;">&lt;/blink&gt;</replacer>

<rewrite title="Remove LOWSRC" oid="11"
 desc="The lowsrc is waste of bandwidth if you have enough of it ;)"
 tag="img">
<attr name="lowsrc"/>
<replace part="attr"/>
</rewrite>

<rewrite title="Remove _blank and _new targets" oid="12"
 desc="Can&apos;t believe I have to make this case-insensitive 8-)">
<attr name="target">(?i)_(blank|new)</attr>
<replace part="attr"/>
</rewrite>

<rewrite title="Layer" oid="13"
 matchurl="eselfilme.de"
 tag="div">
<attr name="id">Layer1</attr>
</rewrite>

<rewrite title="Remove _blank and _new area targets" oid="14"
 tag="area">
<attr name="target">(?i)_(blank|new)</attr>
<replace part="attr"/>
</rewrite>
</folder>
