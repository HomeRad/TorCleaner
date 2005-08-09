<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.40" oid="15" configversion="0.10">
<title lang="en">RSS Feeds</title>

<xmlrewrite sid="wc.41"
 selector="/rdf:RDF/item/description">
  <title lang="en">RDF description</title>
  <description lang="en">Filter HTML in the content of RDF item descriptions.</description>
</xmlrewrite>

<xmlrewrite sid="wc.42"
 selector="/rss/channel/item/description">
  <title lang="en">RSS description</title>
  <description lang="en">Filter HTML in the content of RSS item descriptions.</description>
</xmlrewrite>
</folder>
