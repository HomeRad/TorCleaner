<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Miscellaneous"
 desc="Misc things we dont like in our HTML source :)">

<rewrite title="No meta tags 1"
 desc="Meta tags with name attribute are only for search engines."
 tag="meta">
<attr name="name"/>
<replace part="tag"/>
</rewrite>

<rewrite title="Remove IE shortcut icon"
 desc="Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this."
 tag="link">
<attr name="rel">shortcut icon</attr>
<replace part="tag"/>
</rewrite>

<rewrite title="Remove IFRAMEs"
 desc="&lt;iframe&gt; content is almost always advertising. So remove it."
 tag="iframe">
</rewrite>

<rewrite title="Remove NOFRAMES"
 desc="Most of the browsers have frames so they dont need the &lt;noframes&gt; content."
 tag="noframes">
</rewrite>

<nocomments title="Remove all HTML comments"
 desc="Enable this only if you disable the &lt;script&gt; tag because JavaScript content is often wrapped in a HTML comment!"
 disable="1"/>

<rewrite title="Replace BLINK with B"
 desc="Dont we all hate the &lt;blink&gt; tag?"
 tag="blink">
<replace part="tagname">b</replace>
</rewrite>

<replacer title="The Dude"
 disable="1"
 search="Bastian">The Dude</replacer>

<rewrite title="Tracker images"
 desc="Several sites use 1x1 images to track users."
 tag="img">
<attr name="height">^1$</attr>
<attr name="width">^1$</attr>
</rewrite>
</folder>
