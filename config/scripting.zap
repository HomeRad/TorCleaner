<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.312" oid="8">
<title lang="de">Skripte (Javascript)</title>
<title lang="en">Scripting</title>
<description lang="en">Scripting related.</description>

<rewrite sid="wc.290">
  <title lang="de">Entferne &lt;a&gt; onfocus</title>
  <title lang="en">&lt;a&gt; onfocus</title>
  <attr name="onfocus"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.291">
  <title lang="de">Entferne &lt;a&gt; onmouseout</title>
  <title lang="en">&lt;a&gt; onmouseout</title>
  <attr name="onmouseout"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.292">
  <title lang="de">Entferne &lt;a&gt; onmouseover</title>
  <title lang="en">&lt;a&gt; onmouseover</title>
  <attr name="onmouseover"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.293"
 tag="area">
  <title lang="de">Entferne &lt;area&gt; onfocus</title>
  <title lang="en">&lt;area&gt; onfocus</title>
  <attr name="onfocus"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.294"
 tag="area">
  <title lang="de">Entferne &lt;area&gt; onmouseout</title>
  <title lang="en">&lt;area&gt; onmouseout</title>
  <attr name="onmouseover"/>
  <attr name="onmouseout"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.295"
 tag="area">
  <title lang="de">Entferne &lt;area&gt; onmouseover</title>
  <title lang="en">&lt;area&gt; onmouseover</title>
  <attr name="onmouseover"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.296" disable="1"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; onload</title>
  <title lang="en">&lt;body&gt; onload</title>
  <description lang="en">Remove onload javascript attribute</description>
  <attr name="onload"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.297" disable="1"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; onresize</title>
  <title lang="en">&lt;body&gt; onresize</title>
  <description lang="en">filter the onresize tag</description>
  <attr name="onresize"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.298"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; onunload</title>
  <title lang="en">&lt;body&gt; onunload</title>
  <description lang="en">onunload is used for advert popups</description>
  <attr name="onunload"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.299"
 tag="noscript">
  <title lang="de">Entferne &lt;noscript&gt;</title>
  <title lang="en">&lt;noscript&gt;</title>
  <description lang="de">Entferne das &lt;noscript&gt; tag. Aktivieren Sie diese Regel wenn sie JavaScript zulassen.</description>
  <description lang="en">Remove &lt;noscript&gt; tag (use if you allowed scripting)</description>
</rewrite>

<rewrite sid="wc.300"
 tag="script">
  <title lang="de">Deaktiviere Javascript</title>
  <title lang="en">Disable Javascript</title>
  <description lang="de">Deaktiviere Javascript für bestimmte Seiten.</description>
  <description lang="en">Remove Javascript for certain pages.</description>
  <matchurl>apnews\.excite\.com</matchurl>
</rewrite>

<rewrite sid="wc.301" disable="1">
  <title lang="de">Entferne Javascript Verknüpfungen</title>
  <title lang="en">Remove Javascript links</title>
  <description lang="de">Aktivieren Sie diese Regel nur wenn Sie JavaScript in Ihrem Browser abgeschaltet haben.</description>
  <description lang="en">Only activate this rule if Javascript is disabled in your browser.</description>
  <attr>javascript:.*</attr>
</rewrite>

<rewrite sid="wc.302" disable="1"
 tag="noscript">
  <title lang="de">Benutze &lt;noscript&gt; tag</title>
  <title lang="en">Use noscript tag</title>
  <description lang="de">Aktivieren Sie diese Regel nur wenn Sie JavaScript in Ihrem Browser abgeschaltet haben.</description>
  <description lang="en">Only activate this rule if Javascript is disabled in your browser.</description>
  <replacement part="tag"/>
</rewrite>

<rewrite sid="wc.305"
 tag="frameset">
  <title lang="de">Entferne &lt;frameset&gt; onunload</title>
  <title lang="en">&lt;frameset&gt; onunload</title>
  <description lang="en">onunload is used for advert popups</description>
  <attr name="onunload"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.306"
 tag="frame">
  <title lang="de">Entferne &lt;frame&gt; onunload</title>
  <title lang="en">&lt;frame&gt; onunload</title>
  <description lang="en">onunload is used for advert popups</description>
  <attr name="onunload"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.308"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; ondragstart</title>
  <title lang="en">&lt;body&gt; ondragstart</title>
  <attr name="ondragstart"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.309"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; oncontextmenu</title>
  <title lang="en">&lt;body&gt; oncontextmenu</title>
  <attr name="oncontextmenu"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.311"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; onkeydown</title>
  <title lang="en">&lt;body&gt; onkeydown</title>
  <attr name="onkeydown"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.310"
 tag="body">
  <title lang="de">Entferne &lt;body&gt; onselectstart</title>
  <title lang="en">&lt;body&gt; onselectstart</title>
  <attr name="onselectstart"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.20"
 tag="body">
  <title lang="en">&lt;body&gt; onclick</title>
  <attr name="onclick"/>
  <replacement part="attr"/>
</rewrite>

<rewrite sid="wc.33"
 tag="body">
  <title lang="en">&lt;body&gt; ondblclick</title>
  <attr name="ondblclick"/>
  <replacement part="attr"/>
</rewrite>

<javascript sid="wc.304">
  <title lang="de">Aktiviere JavaScript Filter</title>
  <title lang="en">Activate JavaScript Filter</title>
  <description lang="en">The HTML parser will parse and execute Javascript to remove Popups, and delete JS advertising text written with document.write()</description>
  <nomatchurl>msdn\.microsoft\.com</nomatchurl>
  <nomatchurl>www\.mvhs\.de</nomatchurl>
  <nomatchurl>suprnova\.org</nomatchurl>
  <nomatchurl>www\.litek(-gmbh)?\.de</nomatchurl>
</javascript>

<rewrite sid="wc.307"
 tag="script">
  <title lang="de">Verhindere Rechter-Mausklick kaputtnik</title>
  <title lang="en">Prevent right-click disablement</title>
  <description lang="en">Good! Adaptation, improvisation, but your weakness is not your technique.</description>
  <enclosed>(?i)document\.onmousedown</enclosed>
</rewrite>

<replace sid="wc.303"
 search="top\.location\.href\s*=\s*self\.location\.href">
  <title lang="de">Verhindere Frame-kaputtnik</title>
  <title lang="en">Disable top frame bashing</title>
  <description lang="de">Einige Seiten entfernen umgebende Frames und installieren sich selbst als Hauptframe.</description>
  <description lang="en">Some sites disable surrounding frames and install themselves as the top frame.</description>
</replace>
</folder>
