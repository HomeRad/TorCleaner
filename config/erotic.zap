<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder sid="wc.330" title="Erotic"
 desc="Protect your children from looking erotic sites."
 disable="1" oid="12">
<block sid="wc.326" title="Bad words in the host/path name"
 url="https?://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)"/>

<rewrite sid="wc.328" title="Bad words in the url 1">
<attr>https?://[^/]*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)[^/]*\.(com|org|net|de)</attr>
<replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</rewrite>
</folder>
