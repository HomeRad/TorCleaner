<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.330" oid="12">
<title lang="de">Erotik</title>
<title lang="en">Erotic</title>
<description lang="en">Protect your children from looking erotic sites.</description>

<block sid="wc.326" disable="1"
 url="https?://.*(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)">
  <title lang="de">Erotische W�rter in der URL</title>
  <title lang="en">Bad words in the host/path name</title>
</block>

<htmlrewrite sid="wc.328" disable="1">
  <title lang="de">Erotische W�rter in der URL 2</title>
  <title lang="en">Bad words in the url 1</title>
  <attr>https?://[^/]*\.(naughty|cumshot|lesbian|hardcore|puss(ie|y)|playboy|ficken|penis|xxx|adult|porn)[^/]*\.(com|org|net|de)</attr>
  <replacement part="attrval">http://www.calvinandhobbes.com/</replacement>
</htmlrewrite>
</folder>
