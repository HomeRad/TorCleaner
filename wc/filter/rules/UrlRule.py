# Copyright (C) 2000-2002  Bastian Kleineidam
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

from Rule import Rule

class UrlRule (Rule):
    """rule which applies only to urls which match a regular expression"""
    def __init__ (self, title="No title", desc="", disable=0, matchurl="",
                  dontmatchurl="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.matchurl = matchurl
        self.dontmatchurl = dontmatchurl
        self.attrnames.extend(('matchurl', 'dontmatchurl'))

    def appliesTo (self, url):
        if self.matchurl:
            return self.matchurl.search(url)
        if self.dontmatchurl:
            return not self.dontmatchurl.search(url)
        return 1

    def toxml (self):
        s = Rule.toxml(self)
        if self.matchurl:
            s += '\n matchurl="%s"' % xmlify(self.matchurl)
        if self.dontmatchurl:
            s += '\n dontmatchurl="%s"' % xmlify(self.dontmatchurl)
        return s

    def __str__ (self):
        s = Rule.__str__(self)
        s += "matchurl %s\n" % `self.matchurl`
        s += "dontmatchurl %s\n" % `self.dontmatchurl`
        return s

