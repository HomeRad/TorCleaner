<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.381" oid="6">
<title lang="en">Miscellaneous</title>
<description lang="en">Misc things we dont like in our HTML source :)</description>
<rewrite sid="wc.367"
 tag="meta">
<title lang="en">No meta tags 1</title>
<description lang="en">Meta tags with name attribute are only for search engines.</description>
<attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.368"
 tag="link">
<title lang="en">Remove IE shortcut icon</title>
<description lang="en">Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this.</description>
<attr name="rel">(?i)shortcut icon</attr>
<replacement part="tag"/>
</rewrite>

<rewrite sid="wc.369"
 tag="iframe">
<title lang="en">Remove IFRAMEs</title>
<description lang="en">&lt;iframe&gt; content is almost always advertising. So remove it.</description>
<nomatchurl>www\.eselfilme\.de</nomatchurl>
<nomatchurl>coverviewer\.(sourceforge|sf)\.net</nomatchurl>
</rewrite>


<rewrite sid="wc.370"
 tag="noframes">
<title lang="en">Remove NOFRAMES</title>
<description lang="en">Most of the browsers have frames so they dont need the &lt;noframes&gt; content.</description>
</rewrite>

<nocomments sid="wc.371">
<title lang="en">Remove all HTML comments</title>
<nomatchurl>oreillynet\.com</nomatchurl>
<nomatchurl>www\.onlamp\.com</nomatchurl>
<nomatchurl>www\.onjava\.com</nomatchurl>
</nocomments>

<rewrite sid="wc.372"
 tag="blink">
<title lang="en">Replace BLINK with B</title>
<description lang="en">Dont we all hate the &lt;blink&gt; tag?</description>
<replacement part="tagname">b</replacement>
</rewrite>

<replace sid="wc.373"
 search="text-decoration:\s*blink">
<title lang="en">Replace blink CSS</title>
<description lang="en">Unfuckingbelievable they made a blink CSS entry.</description>
</replace>

<rewrite sid="wc.374"
 tag="marquee">
<title lang="en">Replace MARQUEE with SPAN</title>
<description lang="en">Jeeesus, as if blinking isn&apos;t enough.</description>
<replacement part="tagname">span</replacement>
</rewrite>

<replace sid="wc.375"
 search="(US-Präsident|George( W.)?) Bush">
<title lang="en">Love and Peace</title>
<description lang="en">Love &amp; Peace!</description>
<replacement>Love and Peace</replacement>
</replace>

<rewrite sid="wc.376"
 tag="img">
<title lang="en">Remove LOWSRC</title>
<description lang="en">The lowsrc is waste of bandwidth if you have enough of it ;)</description>
<attr name="lowsrc"/>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.377">
<title lang="en">Remove dumb href targets</title>
<description lang="en">Can&apos;t believe I have to make this case-insensitive 8-)</description>
<attr name="target">(?i)_(blank|new|top)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.378"
 tag="area">
<title lang="en">Remove dumb area targets</title>
<attr name="target">(?i)_(blank|new)</attr>
<replacement part="attr"/>
</rewrite>

<rewrite sid="wc.3">
<title lang="en">Mark href targets</title>
<description lang="en">Display a little marker when links point to unknown targets.</description>
<attr name="target">(?i)^(?!_parent)(.+)$</attr>
<replacement part="attr">target=\1 style=cursor:ne-resize</replacement>
</rewrite>

<rewrite sid="wc.379"
 tag="div">
<title lang="en">Eselfilme layer</title>
<matchurl>eselfilme\.de</matchurl>
<attr name="id">Layer1</attr>
<replacement part="complete"/>
</rewrite>

<replace sid="wc.380"
 disable="1"
 search="Bastian">
<title lang="en">The Dude</title>
<description lang="en">Just a silly example.</description>
<replacement>The Dude</replacement>
</replace>
</folder>
