# -*- coding: iso-8859-1 -*-
"""rule replacing parts of text"""
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

from Rule import compileRegex
from UrlRule import UrlRule
from wc.XmlUtils import xmlquote, xmlquoteattr

class ReplaceRule (UrlRule):
    """This rule can Replace parts of text data according to regular
    expressions"""
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, search="", replacement=""):
        """initialize rule attributes"""
        super(ReplaceRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        self.search = search
        self.replacement = replacement
        self.attrnames.append('search')


    def end_data (self, name):
        super(ReplaceRule, self).end_data(name)
        if name=='replacement':
            self.replacement = self._data


    def compile_data (self):
        """compile url regular expressions"""
        super(ReplaceRule, self).compile_data()
        compileRegex(self, "search")


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromReplaceRule(self)


    def update (self, rule, dryrun=False, log=None):
        """update rule attributes with given rule data"""
        chg = super(ReplaceRule, self).update(rule, dryrun=dryrun, log=log)
        return self.update_attrs(['replacement'], rule, dryrun, log) or chg


    def toxml (self):
        """Rule data as XML for storing"""
	s = super(ReplaceRule, self).toxml()
        if self.search:
            s += '\n search="%s"'%xmlquoteattr(self.search)
        s += ">"
        s += "\n"+self.title_desc_toxml(prefix="  ")
        if self.matchurls or self.nomatchurls:
            s += "\n"+self.matchestoxml(prefix="  ")
        if self.replacement:
            s += '\n  <replacement>%s</replacement>'%xmlquote(self.replacement)
        s += "\n</%s>" % self.get_name()
        return s
