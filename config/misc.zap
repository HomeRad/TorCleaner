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
 tag="iframe">
</rewrite>

<rewrite title="Remove NOFRAMES" oid="3"
 desc="Most of the browsers have frames so they dont need the &lt;noframes&gt; content."
 tag="noframes">
</rewrite>

<nocomments title="Remove all HTML comments" oid="4"/>

<rewrite title="Replace BLINK with B" oid="5"
 desc="Dont we all hate the &lt;blink&gt; tag?"
 tag="blink">
<replace part="tagname">b</replace>
</rewrite>

<replacer title="The Dude" oid="6"
 disable="1"
 search="Bastian">The Dude</replacer>

<rewrite title="Tracker images" oid="7"
 desc="Several sites use 1x1 images to track users."
 tag="img">
<attr name="width">^1$</attr>
<attr name="height">^1$</attr>
</rewrite>

<replacer title="Replace blink CSS" oid="8"
 desc="Unfuckingbelievable they made a blink CSS entry."
 search="text-decoration:\s*blink">text-decoration: none</replacer>

<block title="Statistic trackers" oid="9"
 desc="Some statistic tracker websites"
 scheme=""
 host=".nedstatbasic.net"
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>
</folder>
