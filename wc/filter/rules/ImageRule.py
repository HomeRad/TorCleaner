# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2007 Bastian Kleineidam
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
"""
Filter images by size.
"""

import UrlRule
import wc.XmlUtils


class ImageRule (UrlRule.UrlRule):
    """
    If enabled, tells the Image filter to block certain images.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, width=0, height=0, formats=None, url="",
                  matchurls=None, nomatchurls=None):
        """
        Initalize rule data.
        """
        super(ImageRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.width = width
        self.height = height
        self.intattrs.extend(('width', 'height'))
        self.listattrs.append('formats')
        if formats is None:
            self.formats = []
        else:
            self.formats = formats
        self.url = url
        self.attrnames.extend(('formats', 'url', 'width', 'height'))

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(ImageRule, self).toxml()
        if self.width:
            s += u'\n width="%d"' % self.width
        if self.height:
            s += u'\n height="%d"' % self.height
        if self.formats:
            s += u'\n formats="%s"' % \
                 wc.XmlUtils.xmlquoteattr(",".join(self.formats))
        if self.url:
            s += u'\n url="%s"' % wc.XmlUtils.xmlquoteattr(self.url)
        s += self.endxml()
        return s
