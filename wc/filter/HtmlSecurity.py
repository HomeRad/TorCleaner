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

import os, sys, re
from wc.log import *

_percent_encodings = re.compile('%+').findall
def _has_lots_of_percents (url):
    for match in _percent_encodings(url):
        if len(match) > 10:
            return True
    return False


class HtmlSecurity (object):
    """Scan and repair known security exploits in HTML start/end tags."""
    def __init__ (self):
        self.in_winhelp = False # inside object tag calling WinHelp
        # running on MacOS or MacOSX
        self.macintosh = os.name=='mac' or \
              (os.name=='posix' and sys.platform.startswith('darwin'))


    def scan_start_tag (self, tag, attrs, htmlfilter):
        fun = "%s_start"%tag
        if hasattr(self, fun):
            getattr(self, fun)(attrs, htmlfilter)


    def scan_end_tag (self, tag):
        fun = "%s_end"%tag
        if hasattr(self, fun):
            getattr(self, fun)()


    def input_start (self, attrs, htmlfilter):
        if attrs.has_key('type'):
            # prevent IE crash bug on empty type attribute
            if not attrs['type']:
                warn(FILTER, "%s\n Detected and prevented IE <input type> crash bug", str(htmlfilter))
                del attrs['type']


    def fieldset_start (self, attrs, htmlfilter):
        if attrs.has_key('style'):
            # prevent Mozilla crash bug on fieldsets
            if "position" in attrs['style']:
                warn(FILTER, "%s\n Detected and prevented Mozilla <fieldset style> crash bug", str(htmlfilter))
                del attrs['style']


    def hr_start (self, attrs, htmlfilter):
        if attrs.has_key('align'):
            # prevent CAN-2003-0469, length 50 should be safe
            if len(attrs['align']) > 50:
                warn(FILTER, "%s\n Detected and prevented IE <hr align> crash bug", str(htmlfilter))
                del attrs['align']


    def object_start (self, attrs, htmlfilter):
        if attrs.has_key('type'):
            # prevent CAN-2003-0344, only one / (slash) allowed
            t = attrs['type']
            c = t.count("/")
            if c > 1:
                warn(FILTER, "%s\n Detected and prevented IE <object type> bug", str(htmlfilter))
                t = t.replace("/", "", c-1)
                attrs['type'] = t


    def table_start (self, attrs, htmlfilter):
        if attrs.has_key('width'):
            # prevent CAN-2003-0238, table width=-1 crashes ICQ client
            if attrs['width']=='-1':
                warn(FILTER, "%s\n Detected and prevented ICQ table width crash bug", str(htmlfilter))
                del attrs['width']


    def object_start (self, attrs, htmlfilter):
        if attrs.has_key('codebase'):
            self.in_winhelp = attrs['codebase'].lower().startswith('hhctrl.ocx')


    def object_end (self):
        if self.in_winhelp:
            self.in_winhelp = False


    def param_start (self, attrs, htmlfilter):
        if attrs.has_key('value') and self.in_winhelp:
            # prevent CVE-2002-0823
            if len(attrs['value']) > 50:
                warn(FILTER, "%s\n Detected and prevented WinHlp overflow bug", str(htmlfilter))
                del attrs['value']


    def meta_start (self, attrs, htmlfilter):
        if attrs.has_key('content') and self.macintosh:
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


    def embed_start (self, attrs, htmlfilter):
        if attrs.has_key('src'):
            src = attrs['src']
            if "." in src:
                # prevent CVE-2002-0022
                i = src.rfind('.')
                if len(src[i:]) > 10:
                    warn(FILTER, "%s %s\n Detected and prevented IE filename overflow crash", str(htmlfilter), `src`)
                    del attrs['src']


    def font_start (self, attrs, htmlfilter):
        if attrs.has_key('size'):
            if len(attrs['size']) > 10:
                # prevent CVE-2001-0130
                warn(FILTER, "%s %s\n Detected and prevented Lotus Domino font size overflow crash", str(htmlfilter), `attrs['size']`)
                del attrs['size']


    def a_start (self, attrs, htmlfilter):
        self.check_percent_url(attrs, 'href', htmlfilter)


    def check_percent_url (self, attrs, name, htmlfilter):
        if attrs.has_key(name):
            url = attrs[name]
            if _has_lots_of_percents(url):
                # prevent CAN-2003-0870
                warn(FILTER, "%s %s\n Detected and prevented Opera percent encoding overflow crash", str(htmlfilter), `url`)
                del attrs[name]

