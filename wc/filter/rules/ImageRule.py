# Copyright (C) 2000-2003  Bastian Kleineidam
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

from UrlRule import UrlRule
from wc.XmlUtils import xmlify

class ImageRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, width=0,
                  height=0, type="gif", url="", oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.width=width
        self.height=height
        self.intattrs.extend(('width','height'))
        self.type=type
        self.url = url
        self.attrnames.extend(('type','url','width','height'))

    def fromFactory (self, factory):
        return factory.fromImageRule(self)

    def toxml (self):
        s = UrlRule.toxml(self)
        if self.width:
            s += '\n width="%d"' % self.width
        if self.height:
            s += '\n height="%d"' % self.height
        if self.type!='gif':
            s += '\n type="%s"\n' % self.type
        if self.url:
            return s+">"+xmlify(self.url)+"</image>\n"
        return s+"/>"

