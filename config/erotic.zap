<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Erotic"
 desc="Protect your children from looking erotic sites.">

<block title="Bad words in the host name"
 scheme=""
 host="naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn"
 port=""
 path=""
 parameters=""
 query=""
 fragment=""/>

<block title="Bad words in the path name"
 scheme=""
 host=""
 port=""
 path="naughty|cumshot|lesbian|hardcore|pussie|playboy|ficken|penis|xxx|adult|porn"
 parameters=""
 query=""
 fragment=""/>

<rewrite title="Bad words in the url 1">
<attr>http://.*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn).*\.com</attr>
<replace part="attrval">http://www.calvinandhobbes.com/</replace>
</rewrite>

<rewrite title="Bad words in the url 2">
<attr>http://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)\..*com</attr>
<replace part="attrval">http://www.calvinandhobbes.com/</replace>
</rewrite>
</folder>