<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
<folder title="Redirection and meta" oid="7"
 desc="These are Python specific rules to rewrite some nasty URLs, notably redirections, and get rid of the rest of the meta tags. ">

<rewrite title="No meta tags 2" oid="0"
 desc="Remove all meta tags except redirects. This is only recommended if you REALLY dont want to use &lt;meta http-equiv=&amp;quot;Content-Type&amp;quot;&gt; things. This just leaves the redirections."
 disable="1"
 tag="meta">
<attr name="http-equiv">^(?!(?i)refresh).+</attr>
<replacement part="tag"/>
</rewrite>

<rewrite title="No redirection 1" oid="1"
 desc="location, location, location">
<attr>redirect\.cgi\?.*?location=(?P&lt;replace&gt;[^=&amp;quot;&amp;]+)</attr>
<replacement part="attrval"/>
</rewrite>

<rewrite title="No redirection 2" oid="2"
 desc="redirection at www.nist.gov">
<attr>www\.nist\.gov/cgi-bin/exit_nist\.cgi\?url=(?P&lt;replace&gt;[^=&amp;quot;]+)</attr>
<replacement part="attrval"/>
</rewrite>

<rewrite title="No redirection 3" oid="3"
 desc="redirection at linuxapps.com">
<attr>(linuxapps\.com.*|redir\.asp)\?.*?url=(?P&lt;replace&gt;[^=&amp;quot;&amp;]+)</attr>
<replacement part="attrval"/>
</rewrite>

<rewrite title="No redirection 4" oid="4"
 desc="redirection at fileleech.com">
<attr>www\.fileleech\.com/dl/\?.*?filepath=(?P&lt;replace&gt;[^=&amp;quot;&amp;]+)</attr>
<replacement part="attrval"/>
</rewrite>

<rewrite title="www.coolpix.de" oid="5"
 desc="redirection at coolpix.de">
<attr>www\.cool-pix\.de/cgi-bin/count/count\.pl\?zaehle,(?P&lt;replace&gt;.+)</attr>
<replacement part="attrval"/>
</rewrite>

<rewrite title="Sourceforge Downloads" oid="6"
 desc="Use specific mirror for all SF downloads. Standard is osdn. Choose your own mirror if you dont want this. Available are: Phoenix, AZ, North America (easynews.dl...) Reston, VA, North America (telia.dl...) Chapel Hill, NC, North America (unc.dl...) Minneapolis, MN, North America (umn.dl...) Brookfield, WI, North America (twtelecom.dl...) Brussels, Belgium, Europe (belnet.dl...) Zurich, Switzerland, Europe (swiss.dl...) Prague, Czech Republic, Europe (cesnet.dl...) ">
<attr>http://prdownloads\.sourceforge\.net(?P&lt;value&gt;.+)\?download</attr>
<replacement part="attrval">http://osdn.dl.sourceforge.net%(value)s</replacement>
</rewrite>
</folder>
