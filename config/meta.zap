<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.22" oid="14">
<title lang="de">HTML Metadaten</title>
<title lang="en">HTML Metadata</title>

<rewrite sid="wc.23"
 tag="meta">
  <title lang="de">Keine Namensinformation</title>
  <description lang="de">Der Name in den Metadaten ist nur für Suchmaschinen interessant.</description>
  <attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
</rewrite>

<rewrite sid="wc.24" disable="1"
 tag="meta">
  <title lang="de">Alles außer refresh</title>
  <description lang="de">Lösche alle Meta-Informationen außer Weiterleitungen. Dies ist nicht empfehlenswert und nur zu Testzwecken hier.</description>
  <attr name="http-equiv">^(?!(?i)refresh).+</attr>
</rewrite>
</folder>
