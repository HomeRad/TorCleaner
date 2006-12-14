<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.289" oid="8" configversion="0.10">
<title lang="de">Plugins und Medien</title>
<title lang="en">Plugins</title>
<description lang="en">The filter rules found here remove plugin (eg flash) contents, but only for selected sites.</description>

<htmlrewrite sid="wc.288"
 tag="object">
  <title lang="de">Entferne OBJECT Daten</title>
  <title lang="en">Remove OBJECTs</title>
  <description lang="de">Entferne alle mit &lt;object&gt; eingebundenen Inhalte.</description>
  <description lang="en">Kill &lt;object&gt; things.</description>
  <matchurl>www\.heise\.de</matchurl>
  <matchurl>www\.hartware\.de</matchurl>
  <matchurl>\.imdb\.com</matchurl>
</htmlrewrite>

<htmlrewrite sid="wc.287"
 tag="embed">
  <title lang="de">Entferne EMBED Daten</title>
  <title lang="en">Remove EMBEDded content</title>
  <description lang="de">Entferne alle mit &lt;embed&gt; eingebundenen Daten.</description>
  <description lang="en">Kill &lt;embed&gt; things.</description>
  <matchurl>www\.heise\.de</matchurl>
</htmlrewrite>

<htmlrewrite sid="wc.39"
 tag="embed">
  <title lang="de">Entferne embed loops</title>
  <title lang="en">Remove EMBED loops</title>
  <attr name="loop">true</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.43"
 tag="embed">
  <title lang="en">Disable EMBED autostart</title>
  <attr name="autostart">(?i)true</attr>
  <replacement part="attrval">false</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.44"
 tag="embed">
  <title lang="en">Disable EMBED hidden</title>
  <attr name="hidden">(?i)true</attr>
  <replacement part="attrval">false</replacement>
</htmlrewrite>
</folder>
