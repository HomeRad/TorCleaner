<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.22" oid="15" configversion="0.10">
<title lang="de">HTML Metadaten</title>
<title lang="en">HTML Metadata</title>

<htmlrewrite sid="wc.23"
 tag="meta">
  <title lang="de">Keine Namensinformation</title>
  <title lang="en">No name information</title>
  <description lang="de">Der Name in den Metadaten ist nur für Suchmaschinen interessant.</description>
  <description lang="en">The name in meta data is only interesting for search engines.</description>
  <attr name="name">(?i)(author|description|keywords|revisit-after|page-topic|url|allow-search|searchtitle|robots|audience|content-language|copyright|MSSmartTagsPreventParsing)</attr>
  <replacement part="complete"/>
</htmlrewrite>

<htmlrewrite sid="wc.24" disable="1"
 tag="meta">
  <title lang="de">Alles außer refresh</title>
  <title lang="en">Remove everything except refresh</title>
  <description lang="de">Lösche alle Meta-Informationen außer Weiterleitungen. Dies ist nicht empfehlenswert und nur zu Testzwecken hier.</description>
  <description lang="en">Remove every meta data except refreshes. This is not recommended.</description>
  <attr name="http-equiv">^(?!(?i)refresh).+</attr>
  <replacement part="complete"/>
</htmlrewrite>
</folder>
