<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Erotic" oid="2"
 desc="Protect your children from looking erotic sites."
 disable="1">

<block title="Bad words in the host name" oid="0"
 scheme=""
 host="naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn"
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<block title="Bad words in the path name" oid="1"
 scheme=""
 host=""
 port=""
 path="naughty|cumshot|lesbian|hardcore|pussie|playboy|ficken|penis|xxx|adult|porn"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Bad words in the url 1" oid="2">
<attr>http://.*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn).*\.com</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>

<rewrite title="Bad words in the url 2" oid="3">
<attr>http://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)\..*com</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>
</folder>
