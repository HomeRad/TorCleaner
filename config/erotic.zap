<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.330" oid="12" title="Erotic"
 desc="Protect your children from looking erotic sites."
 disable="1">

<block sid="wc.326" oid="0" title="Bad words in the host name"
 scheme=""
 host="naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn"
 port=""
 path=""
 query=""
 fragment=""/>

<block sid="wc.327" oid="1" title="Bad words in the path name"
 scheme=""
 host=""
 port=""
 path="naughty|cumshot|lesbian|hardcore|pussie|playboy|ficken|penis|xxx|adult|porn"
 query=""
 fragment=""/>

<rewrite sid="wc.328" oid="2" title="Bad words in the url 1">
<attr>http://.*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn).*\.com</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>

<rewrite sid="wc.329" oid="3" title="Bad words in the url 2">
<attr>http://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)\..*com</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>
</folder>
