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

import wc, time
reload(wc)
wc.DebugLevel = 0
wc.config = wc.Configuration()
wc.config['filters'] = ['Replacer']
wc.config.init_filter_modules()
start = time.clock()
attrs = wc.filter.initStateObjects(url="")
filtered = wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY,
           htmldata, 'finish', attrs)
stop = time.clock()
print filtered
#print "time: %.3f seconds" % (stop-start)
