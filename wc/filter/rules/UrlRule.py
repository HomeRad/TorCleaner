# -*- coding: iso-8859-1 -*-
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

from Rule import Rule
from wc.XmlUtils import xmlify
from wc.log import *

class UrlRule (Rule):
    """rule which applies only to urls which match a regular expression"""
    def __init__ (self, sid=None, title="No title", desc="",
                  disable=0, matchurl="", dontmatchurl=""):
        super(UrlRule, self).__init__(sid=sid, title=title,
                                      desc=desc, disable=disable)
        self.matchurl = matchurl
        self.dontmatchurl = dontmatchurl
        self.attrnames.extend(('matchurl', 'dontmatchurl'))


    def appliesTo (self, url):
        if self.matchurl:
            return self.matchurl_ro.search(url)
        if self.dontmatchurl:
            return not self.dontmatchurl_ro.search(url)
        return True


    def toxml (self):
        s = super(UrlRule, self).toxml()
        if self.matchurl:
            s += '\n matchurl="%s"' % xmlify(self.matchurl)
        if self.dontmatchurl:
            s += '\n dontmatchurl="%s"' % xmlify(self.dontmatchurl)
        return s


    def __str__ (self):
        return super(UrlRule, self).__str__() + \
            "matchurl %r\n" % self.matchurl + \
            "dontmatchurl %r\n" % self.dontmatchurl
