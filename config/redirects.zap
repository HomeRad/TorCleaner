<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.389" oid="10">
<title lang="de">Weiterleitungen</title>
<title lang="en">Redirection and meta</title>
<description lang="en">These are Python specific rules to rewrite some nasty URLs, notably redirections, and get rid of the rest of the meta tags.</description>

<rewrite sid="wc.383">
  <title lang="en">No redirection 1</title>
  <description lang="en">location, location, location</description>
  <attr>redirect\.cgi\?.*?location=([^=&amp;quot;&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.384">
  <title lang="en">No redirection 2</title>
  <description lang="en">redirection at www.nist.gov</description>
  <attr>www\.nist\.gov/cgi-bin/exit_nist\.cgi\?url=([^=&amp;quot;]+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.385">
  <title lang="en">No redirection 3</title>
  <description lang="en">redirection at linuxapps.com</description>
  <attr>(linuxapps\.com.*|redir\.asp)\?.*?url=([^=&amp;quot;&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.386">
  <title lang="en">No redirection 4</title>
  <description lang="en">redirection at fileleech.com</description>
  <attr>www\.fileleech\.com/dl/\?.*?filepath=([^=&amp;quot;&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.387">
  <title lang="en">www.coolpix.de</title>
  <description lang="en">redirection at coolpix.de</description>
  <attr>www\.cool-pix\.de/cgi-bin/count/count\.pl\?zaehle,(.+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.388">
  <title lang="en">Sourceforge Downloads</title>
  <description lang="en">Use specific mirror for all SF downloads. Standard is osdn. Choose your own mirror if you dont want this. Available are: Phoenix, AZ, North America (easynews.dl...) Reston, VA, North America (telia.dl...) Chapel Hill, NC, North America (unc.dl...) Minneapolis, MN, North America (umn.dl...) Brookfield, WI, North America (twtelecom.dl...) Brussels, Belgium, Europe (belnet.dl...) Zurich, Switzerland, Europe (swiss.dl...) Prague, Czech Republic, Europe (cesnet.dl...) </description>
  <attr>http://prdownloads\.sourceforge\.net(.+)\?download</attr>
  <replacement part="attrval">http://osdn.dl.sourceforge.net\1</replacement>
</rewrite>

<rewrite sid="wc.13">
  <title lang="en">Knoppix redirection</title>
  <matchurl>knopper\.net</matchurl>
  <attr>download\.php3\?link=([^=&amp;quot;&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>

<rewrite sid="wc.4">
  <title lang="en">dockapps.org</title>
  <description lang="en">dockapps</description>
  <attr>http://www\.dockapps\.org/click\.php\?send=(.+)</attr>
  <replacement part="attrval">\1</replacement>
</rewrite>
</folder>
