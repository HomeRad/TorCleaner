# -*- coding: iso-8859-1 -*-
"""image reducer config rule"""
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

import wc.filter.rules.UrlRule


class ImageReduceRule (wc.filter.rules.UrlRule.UrlRule):
    """configures the image reducer filter (if enabled)"""

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, quality=20, minimal_size_bytes=5120,
                  matchurls=[], nomatchurls=[]):
        """initalize rule data"""
        super(ImageReduceRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.quality = quality
        self.minimal_size_bytes = minimal_size_bytes
        self.attrnames.extend(('quality', 'minimal_size_bytes'))


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromImageReduceRule(self)


    def toxml (self):
        """Rule data as XML for storing"""
        s = super(ImageReduceRule, self).toxml()
        if self.width:
            s += u'\n quality="%d"' % self.quality
        if self.height:
            s += u'\n minimal_size_bytes="%d"' % self.minimal_size_bytes
        s += u">"
        s += u"\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.get_name()
        return s
