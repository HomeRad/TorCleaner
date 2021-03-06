<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.381" oid="9">
<title lang="de">Verschiedenes</title>
<title lang="en">Miscellaneous</title>
<description lang="en">Misc things we dont like in our HTML source :)</description>

<htmlrewrite sid="wc.368"
 tag="link">
  <title lang="de">Entferne wummel favicon</title>
  <title lang="en">Remove favicon</title>
  <description lang="de">Einige Hui HTML Seiten liefern ein kleines Icon welches neben der URL angezeigt werden soll. Diese Regel verhindert dies.</description>
  <description lang="en">Some HTML pages supply a link to a favicon.gif icon image and it gets loaded automatically.</description>
  <attr name="rel">(?i)shortcut\s+icon</attr>
  <replacement part="tag"/>
</htmlrewrite>

<htmlrewrite sid="wc.369"
 tag="iframe">
  <title lang="de">Entferne &lt;iframe&gt;</title>
  <title lang="en">Remove &lt;iframe&gt;</title>
  <description lang="de">&lt;iframe&gt; Inhalte sind fast immer Werbungen.</description>
  <description lang="en">&lt;iframe&gt; content is almost always advertising.</description>
  <nomatchurl>www\.eselfilme\.de</nomatchurl>
  <nomatchurl>coverviewer\.(sourceforge|sf)\.net</nomatchurl>
</htmlrewrite>

<htmlrewrite sid="wc.370"
 tag="noframes">
  <title lang="de">Entferne &lt;noframes&gt;</title>
  <title lang="en">Remove &lt;noframes&gt;</title>
  <description lang="en">Most of the browsers have frames so they dont need the &lt;noframes&gt; content.</description>
</htmlrewrite>

<nocomments sid="wc.371">
  <title lang="de">Entferne HTML Kommentare</title>
  <title lang="en">Remove all HTML comments</title>
  <nomatchurl>oreillynet\.com</nomatchurl>
  <nomatchurl>www\.onlamp\.com</nomatchurl>
  <nomatchurl>www\.onjava\.com</nomatchurl>
</nocomments>

<htmlrewrite sid="wc.372"
 tag="blink">
  <title lang="de">Ersetze &lt;blink&gt; durch &lt;b&gt;</title>
  <title lang="en">Replace &lt;blink&gt; with &lt;b&gt;</title>
  <description lang="de">&lt;blink&gt; &lt;blink&gt;</description>
  <description lang="en">Dont we all hate the &lt;blink&gt; tag?</description>
  <replacement part="tagname">b</replacement>
</htmlrewrite>

<replace sid="wc.373"
 search="text-decoration:\s*blink">
  <title lang="de">Ersetze blink CSS</title>
  <title lang="en">Replace blink CSS</title>
  <description lang="de">Unglaublich dass es ein CSS blink Attribut gibt.</description>
  <description lang="en">Unfuckingbelievable they made a blink CSS entry.</description>
</replace>

<htmlrewrite sid="wc.374"
 tag="marquee">
  <title lang="de">Ersetze &lt;marquee&gt; mit &lt;span&gt;</title>
  <title lang="en">Replace &lt;marquee&gt; with &lt;span&gt;</title>
  <description lang="de">Als ob blink nicht schon genug w�re.</description>
  <description lang="en">Jeeesus, as if blinking isn&apos;t enough.</description>
  <replacement part="tagname">span</replacement>
</htmlrewrite>

<replace sid="wc.375"
 search="(US-Pr�sident|George( W.)?) Bush">
  <title lang="en">Love and Peace</title>
  <description lang="de">Friede Freude Eierkuchen</description>
  <description lang="en">Love &amp; Peace!</description>
  <replacement>Love and Peace</replacement>
</replace>

<htmlrewrite sid="wc.376"
 tag="img">
  <title lang="de">Entferne &lt;lowsrc&gt;</title>
  <title lang="en">Remove &lt;lowsrc&gt;</title>
  <description lang="de">Falls man genug Bandbreite besitzt, ist lowsrc eine Verschwendung :)</description>
  <description lang="en">The lowsrc is waste of bandwidth if you have enough of it ;)</description>
  <attr name="lowsrc"/>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.377">
  <title lang="de">Entferne &lt;href&gt; targets</title>
  <title lang="en">Remove &lt;href&gt; targets</title>
  <description lang="en">Can&apos;t believe I have to make this case-insensitive 8-)</description>
  <attr name="target">(?i)_(blank|new|top)</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.378"
 tag="area">
  <title lang="de">Entferne &lt;area&gt; targets</title>
  <title lang="en">Remove &lt;area&gt; targets</title>
  <attr name="target">(?i)_(blank|new)</attr>
  <replacement part="attr"/>
</htmlrewrite>

<htmlrewrite sid="wc.379"
 tag="div">
  <title lang="en">Eselfilme layer</title>
  <matchurl>eselfilme\.de</matchurl>
  <attr name="id">Layer1</attr>
</htmlrewrite>

<htmlrewrite sid="wc.3">
  <title lang="de">Markiere &lt;href&gt; targets</title>
  <title lang="en">Mark &lt;href&gt; targets</title>
  <description lang="de">Ver�ndere den Mauszeiger wenn Verkn�pfungen ein neues Fenster �ffnen.</description>
  <description lang="en">Display a little marker when links point to unknown targets.</description>
  <attr name="target">(?i)^(?!_parent)(.+)$</attr>
  <replacement part="attr">target=\1 style=cursor:ne-resize</replacement>
</htmlrewrite>

<replace sid="wc.380" disable="0"
 search="Bastian">
  <title lang="en">The Dude</title>
  <description lang="de">Nur ein kleines Bespiel</description>
  <description lang="en">Just a silly example.</description>
  <replacement>The Dude</replacement>
</replace>
</folder>
