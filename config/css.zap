<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.362" oid="11" configversion="0.10">
<title lang="de">CSS Filter</title>
<title lang="en">CSS filtering</title>
<description lang="en">Some browsers do not support CSS, so turn it off with these rules. Or you can test your pages without  CSS styles!  Well, we remove only complete &lt;style&gt; tags, not style="" attributes.</description>

<htmlrewrite sid="wc.361" disable="1"
 tag="style">
  <title lang="de">Entferne STYLE tag</title>
  <title lang="en">Remove STYLE tag</title>
  <description lang="de">Entferne das &lt;style&gt; tag.</description>
  <description lang="en">Remove the &lt;style&gt; tag.</description>
</htmlrewrite>

<htmlrewrite sid="wc.78"
 tag="div">
  <title lang="de">Entferne display:none</title>
  <attr name="style">display:\s*none</attr>
</htmlrewrite>
</folder>
