<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.330"
 disable="1" oid="12">
<title lang="en">Erotic</title>
<description lang="en">Protect your children from looking erotic sites.</description>
<block sid="wc.326"
 url="https?://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)">
<title lang="en">Bad words in the host/path name</title>
</block>
<rewrite sid="wc.328">
<title lang="en">Bad words in the url 1</title>
<attr>https?://[^/]*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)[^/]*\.(com|org|net|de)</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>
</folder>
