# -*- coding: iso-8859-1 -*-
""" test script to test filtering"""

htmldata = """
<script type="text/javascript" defer>
<!-- Hide code for older browsers...
// window instance
document.write("<OBJECT");	
document.write("CLASSID=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\"");
document.write("CODEBASE=\"http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=4,0,0,0\"");
document.write("ID=\"triplex_intro\" WIDTH=\"18\" HEIGHT=\"18\"\>");
document.write("<PARAM NAME=\"movie\" VALUE=\"flash_chk.swf\"\>");
document.write("<PARAM NAME=\"menu\" VALUE=\"false\"\>");
document.write("<PARAM NAME=\"quality\" VALUE=\"best\">");
document.write("<PARAM NAME=\"bgcolor\" VALUE=\"#FFFFFF\">");
document.write("<EMBED SRC=\"flash_chk.swf\" MENU=\"false\"");
document.write("QUALITY=\"best\" BGCOLOR=\"#FFFFFF\" WIDTH=\"18\" HEIGHT=\"18\" TYPE=\"application/x-shockwave-flash\"");
document.write("PLUGINSPAGE=\"http://www.macromedia.com/shockwave/download/index.cgi?p1_prod_version=shockwaveflash\">");
document.write("</OBJECT>");
// end of script. -->
</script>
"""

from test import initlog
initlog("test/logging.conf")
import wc
wc.config = wc.Configuration()
wc.config['filters'] = ['Replacer']
wc.config.init_filter_modules()
import time
from wc.filter import applyfilter, get_filterattrs, FILTER_RESPONSE_MODIFY
attrs = get_filterattrs("", [FILTER_RESPONSE_MODIFY])
print applyfilter(FILTER_RESPONSE_MODIFY, htmldata, 'finish', attrs)
