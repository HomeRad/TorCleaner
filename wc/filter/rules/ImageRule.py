# -*- coding: iso-8859-1 -*-
"""filter images by size"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, width=0, height=0, formats=[], url=""):
        """initalize rule data"""
        super(ImageRule, self).__init__(sid=sid, titles=titles,
                                  descriptions=descriptions, disable=disable)
        self.width = width
        self.height = height
        self.intattrs.extend(('width','height'))
        self.listattrs.append('formats')
        self.formats = formats
        self.url = url
        self.attrnames.extend(('formats','url','width','height'))


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromImageRule(self)


    def toxml (self):
        """Rule data as XML for storing"""
        s = super(ImageRule, self).toxml()
        if self.width:
            s += '\n width="%d"' % self.width
        if self.height:
            s += '\n height="%d"' % self.height
        if self.formats:
            s += '\n formats="%s"' % xmlify(",".join(self.formats))
        if self.url:
            s += '\n url="%s"' % xmlify(self.url)
        s += ">"
        s += "\n"+self.title_desc_toxml(prefix="  ")
        if self.matchurls or self.nomatchurls:
            s += "\n"+self.matchestoxml(prefix="  ")
        s += "\n</%s>" % self.get_name()
        return s
