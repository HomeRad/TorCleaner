<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.381" oid="6" title="Miscellaneous 2"
 desc="Misc ö things we dont like in our HTML source :)">

<rewrite sid="wc.368" oid="0" title="Remove IE shortcut icon"
 desc="Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically from Internet Explorer. Some people dont like this."
 tag="link">
<attr name="rel">(?i)shortcut icon</attr>
</rewrite>

<rewrite sid="wc.367" oid="1" title="No meta tags"
 desc="Meta tags with name attribute are only for search engines."
 tag="meta">
<attr name="name">(?i)(author|desc|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
<replacement part="tag"/>
</rewrite>

<replace sid="wc.380" oid="13" title="The Dude"
 desc="Just a silly example."
 disable="1"
 search="Wummel"/>

<replace sid="wc.980" oid="14" title="The Dude"
 desc="Just a silly example."
 disable="1"
 search="Imadoofus"/>

<replace sid="us.980" oid="15" title="The Dude"
 desc="Just a silly example."
 disable="1"
 search="Ignoring"/>
</folder>
