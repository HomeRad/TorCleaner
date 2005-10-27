<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.40" oid="15" configversion="0.10">
<title lang="en">RSS Feeds</title>

<xmlrewrite sid="wc.41"
 selector="/rdf:RDF/item/description"
 replacetype="rsshtml">
  <title lang="en">RDF description</title>
  <description lang="en">Filter HTML in the content of RDF item descriptions.</description>
</xmlrewrite>

<xmlrewrite sid="wc.42"
 selector="/rss/channel/item/description"
 replacetype="rsshtml">
  <title lang="en">RSS description</title>
  <description lang="en">Filter HTML in the content of RSS item descriptions.</description>
</xmlrewrite>

<replace sid="wc.46"
 search="(?s)Advertisement.*&lt;/a&gt;">
  <title lang="en">Securityfocus ad</title>
  <matchurl>securityfocus\.org/rss</matchurl>
</replace>

<htmlrewrite sid="wc.45">
  <title lang="en">OSDN RSS ads</title>
  <description lang="en">Ads in RSS feeds of freshmeat and slashdot.</description>
  <attr>http://rss\.(slashdot\.org|freshmeat\.net)/~[ca]/(Slashdot|freshmeat)/</attr>
</htmlrewrite>
</folder>
