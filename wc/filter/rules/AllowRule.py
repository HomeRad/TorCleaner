# -*- coding: iso-8859-1 -*-
"""block urls"""
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

import wc.filter.rules.UrlRule
import wc.XmlUtils


class AllowRule (wc.filter.rules.UrlRule.UrlRule):
    """Define a regular expression for urls to be allowed, even if they
       would be blocked by a block rule otherwise.
       See also the Blocker filter module.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, url="", matchurls=[], nomatchurls=[]):
        """initialize rule data"""
        super(AllowRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.url = url
        self.attrnames.append('url')

    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromAllowRule(self)

    def toxml (self):
        """Rule data as XML for storing"""
        s =  super(AllowRule, self).toxml() + \
             u'\n url="%s">' % wc.XmlUtils.xmlquoteattr(self.url)
        s += u"\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.get_name()
        return s
