"""filter security flaws out of HTML tags."""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys
from wc.log import *

class HtmlSecurity (object):
    """Scan and repair known security exploits in HTML start/end tags.
       XXX would be fixed with file(1) like scanning of documents and
       fixing of the content-type header value:
         CVE-2002-0025
         CVE-2002-0024
       """
    def __init__ (self):
        self.in_winhelp = False # inside object tag calling WinHelp
        # running on MacOS or MacOSX
        self.macintosh = os.name=='mac' or \
              (os.name=='posix' and sys.platform.startswith('darwin'))


    def scan_start_tag (self, tag, attrs, htmlfilter):
        if tag=="input" and attrs.has_key('type'):
            # prevent IE crash bug on empty type attribute
            if not attrs['type']:
                warn(FILTER, "%s\n Detected and prevented IE <input type> crash bug", str(htmlfilter))
                del attrs['type']
        elif tag=="fieldset" and attrs.has_key('style'):
            # prevent Mozilla crash bug on fieldsets
            if "position" in attrs['style']:
                warn(FILTER, "%s\n Detected and prevented Mozilla <fieldset style> crash bug", str(htmlfilter))
                del attrs['style']
        elif tag=="hr" and attrs.has_key('align'):
            # prevent CAN-2003-0469, length 50 should be safe
            if len(attrs['align']) > 50:
                warn(FILTER, "%s\n Detected and prevented IE <hr align> crash bug", str(htmlfilter))
                del attrs['align']
        elif tag=="object" and attrs.has_key('type'):
            # prevent CAN-2003-0344, only one / (slash) allowed
            t = attrs['type']
            c = t.count("/")
            if c > 1:
                warn(FILTER, "%s\n Detected and prevented IE <object type> bug", str(htmlfilter))
                t = t.replace("/", "", c-1)
                attrs['type'] = t
        elif tag=='table' and attrs.has_key('width'):
            # prevent CAN-2003-0238, table width=-1 crashes ICQ client
            if attrs['width']=='-1':
                warn(FILTER, "%s\n Detected and prevented ICQ table width crash bug", str(htmlfilter))
                del attrs['width']
        elif tag=='object' and attrs.has_key('codebase'):
            self.in_winhelp = attrs['codebase'].lower().startswith('hhctrl.ocx')
        elif tag=='param' and attrs.has_key('value') and self.in_winhelp:
            # prevent CVE-2002-0823
            if len(attrs['value']) > 50:
                warn(FILTER, "%s\n Detected and prevented WinHlp overflow bug", str(htmlfilter))
                del attrs['value']
        elif tag=='meta' and attrs.has_key('content') and self.macintosh:
            # prevent CVE-2002-0153
            if attrs.get('http-equiv', '').lower()=='refresh':
                url = attrs['content'].lower()
                if ";" in url:
                    url = url.split(";", 1)[1]
                if url.startswith('url='):
                    url = url[4:]
                if url.startswith('file:/'):
                    warn(FILTER, "%s %s\n Detected and prevented local file redirection", str(htmlfilter), `attrs['content']`)
                    del attrs['content']
        elif tag=='embed' and attrs.has_key('src'):
            src = attrs['src']
            if "." in src:
                # prevent CVE-2002-0022
                i = src.find('.')
                if len(src[i:]) > 10:
                    warn(FILTER, "%s %s\n Detected and prevented IE filename overflow crash", str(htmlfilter), `src`)
                    del attrs['src']
        elif tag=='font' and attrs.has_key('size'):
            if len(attrs['size']) > 10:
                # prevent CVE-2001-0130
                warn(FILTER, "%s %s\n Detected and prevented Lotus Domino font size overflow crash", str(htmlfilter), `attrs['size']`)
                del attrs['size']


    def scan_end_tag (self, tag):
        if self.in_winhelp and tag=='object':
            self.in_winhelp = False
