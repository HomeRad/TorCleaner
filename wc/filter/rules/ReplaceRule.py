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
Rule replacing parts of text.
"""

import UrlRule
import Rule
import wc.XmlUtils


class ReplaceRule (UrlRule.UrlRule):
    """
    This rule can Replace parts of text data according to regular expressions.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, search="", replacement=""):
        """
        Initialize rule attributes.
        """
        super(ReplaceRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        self.search = search
        self.replacement = replacement
        self.attrnames.append('search')

    def end_data (self, name):
        """
        Store replacement data.
        """
        super(ReplaceRule, self).end_data(name)
        if name == 'replacement':
            self.replacement = self._data

    def compile_data (self):
        """
        Compile url regular expressions.
        """
        super(ReplaceRule, self).compile_data()
        Rule.compileRegex(self, "search")

    def update (self, rule, dryrun=False, log=None):
        """
        Update rule attributes with given rule data.
        """
        chg = super(ReplaceRule, self).update(rule, dryrun=dryrun, log=log)
        return self.update_attrs(['replacement'], rule, dryrun, log) or chg

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(ReplaceRule, self).toxml()
        if self.search:
            s += u'\n search="%s"' % wc.XmlUtils.xmlquoteattr(self.search)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.replacement:
            s += u'\n  <replacement>%s</replacement>' % \
              wc.XmlUtils.xmlquote(self.replacement)
        s += u"\n</%s>" % self.name
        return s
