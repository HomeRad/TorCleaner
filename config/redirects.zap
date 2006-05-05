<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
<folder sid="wc.389" oid="10" configversion="0.10">
<title lang="de">Weiterleitungen</title>
<title lang="en">Redirections</title>
<description lang="en">Regeln gegen Weiterleitungen.</description>

<htmlrewrite sid="wc.383"
 tag="a">
  <title lang="de">redirect.cgi Weiterleitung</title>
  <title lang="en">redirect.cgi redirect</title>
  <attr name="href">redirect\.cgi\?.*?location=(?P&lt;url&gt;[^="&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.384"
 tag="a">
  <title lang="de">www.nist.gov Weiterleitung</title>
  <title lang="en">www.nist.gov redirect</title>
  <attr name="href">www\.nist\.gov/cgi-bin/exit_nist\.cgi\?url=(?P&lt;url&gt;[^="]+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.385"
 tag="a">
  <title lang="de">linuxapps.com Weiterleitung</title>
  <title lang="en">linuxapps.com redirect</title>
  <attr name="href">(linuxapps\.com.*|redir\.asp)\?.*?url=(?P&lt;url&gt;[^="&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.386"
 tag="a">
  <title lang="de">fileleech.com Weiterleitung</title>
  <title lang="en">fileleech.com redirect</title>
  <attr name="href">www\.fileleech\.com/dl/\?.*?filepath=(?P&lt;url&gt;[^="&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.387"
 tag="a">
  <title lang="de">coolpix.de Weiterleitung</title>
  <title lang="en">coolpix.de redirect</title>
  <attr name="href">www\.cool-pix\.de/cgi-bin/count/count\.pl\?zaehle,(?P&lt;url&gt;.+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.388"
 tag="a">
  <title lang="de">Sourceforge Downloads</title>
  <title lang="en">Sourceforge Downloads</title>
  <description lang="en">Use specific mirror for all SF downloads. Standard is osdn. Choose your own mirror if you dont want this. Available are: Phoenix, AZ, North America (easynews.dl...) Reston, VA, North America (telia.dl...) Chapel Hill, NC, North America (unc.dl...) Minneapolis, MN, North America (umn.dl...) Brookfield, WI, North America (twtelecom.dl...) Brussels, Belgium, Europe (belnet.dl...) Zurich, Switzerland, Europe (swiss.dl...) Prague, Czech Republic, Europe (cesnet.dl...) </description>
  <attr name="href">http://prdownloads\.sourceforge\.net(.+)\?download</attr>
  <replacement part="attrval">http://osdn.dl.sourceforge.net\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.50"
 tag="a">
  <title lang="de">Berlios Downloads</title>
  <title lang="en">Berlios Downloads</title>
  <description lang="en">Use specific mirror for all Berlios downloads.Available are download and download2.</description>
  <attr name="href">http://prdownload\.berlios\.de(.+)</attr>
  <replacement part="attrval">http://download.berlios.de\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.13"
 tag="a">
  <title lang="de">Knoppix Weiterleitung</title>
  <title lang="en">Knoppix redirection</title>
  <matchurl>knopper\.net</matchurl>
  <attr name="href">download\.php3\?link=(?P&lt;url&gt;[^="&amp;]+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.4"
 tag="a">
  <title lang="en">dockapps.org Weiterleitung</title>
  <attr name="href">http://www\.dockapps\.org/click\.php\?send=(?P&lt;url&gt;.+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.79"
 tag="a">
  <title lang="de">anonym.to Weiterleitung</title>
  <title lang="en">anonym.to redirect</title>
  <attr name="href">http://anonym\.to/\?(?P&lt;url&gt;.+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.82"
 tag="a">
  <title lang="de">alexa Weiterleitung</title>
  <title lang="en">alexa redirect</title>
  <matchurl>alexa\.com</matchurl>
  <attr name="href">http://redirect\.alexa\.com/redirect\?(?P&lt;url&gt;.+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>

<htmlrewrite sid="wc.51"
 tag="img">
  <title lang="de">anonymizer.com Weiterleitung</title>
  <attr name="src">http://invis\.free\.anonymizer\.com/(?P&lt;url&gt;.+)</attr>
  <replacement part="attrval">\1</replacement>
</htmlrewrite>
</folder>
