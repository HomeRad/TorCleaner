<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Redirection and meta"
 desc="These are Python specific rules to rewrite some nasty URLs, notably redirections, and get rid of the rest of the meta tags.">

<rewrite title="No meta tags 2"
 desc="Remove all meta tags except redirects. This is only recommended if you REALLY dont want to use &lt;meta http-equiv=&quot;Content-Type&quot;&gt; things. This just leaves the redirections."
 disable="1"
 tag="meta">
<attr name="http-equiv">^(?!(?i)refresh).+</attr>
<replace part="tag"/>
</rewrite>

<rewrite title="No redirection 1"
 desc="location, location, location">
<attr>redirect\.cgi\?.*?location=(?P&lt;replace&gt;[^=&quot;&amp;]+)</attr>
<replace part="attrval"/>
</rewrite>

<rewrite title="No redirection 2"
 desc="redirection at www.nist.gov">
<attr>www\.nist\.gov/cgi-bin/exit_nist\.cgi\?url=(?P&lt;replace&gt;[^=&quot;]+)</attr>
<replace part="attrval"/>
</rewrite>

<rewrite title="No redirection 3"
 desc="redirection at linuxapps.com">
<attr>(linuxapps\.com.*|redir\.asp)\?.*?url=(?P&lt;replace&gt;[^=&quot;&amp;]+)</attr>
<replace part="attrval"/>
</rewrite>

<rewrite title="No redirection 4">
<attr>www\.fileleech\.com/dl/\?.*?filepath=(?P&lt;replace&gt;[^=&quot;&amp;]+)</attr>
<replace part="attrval"/>
</rewrite>

<rewrite title="www.coolpix.de">
<attr>www\.cool-pix\.de/cgi-bin/count/count\.pl\?zaehle,(?P&lt;replace&gt;.+)</attr>
<replace part="attrval"/>
</rewrite>
</folder>