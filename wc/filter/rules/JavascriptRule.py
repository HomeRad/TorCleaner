# -*- coding: iso-8859-1 -*-
"""filter javascript"""
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

class JavascriptRule (wc.filter.rules.UrlRule.UrlRule):
    """if enabled, this rule tells the Rewriter to filter JavaScript"""

    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromJavascriptRule(self)


    def toxml (self):
        """Rule data as XML for storing"""
        s = super(JavascriptRule, self).toxml()+">"
        s += "\n"+self.title_desc_toxml(prefix="  ")
        if self.matchurls or self.nomatchurls:
            s += "\n"+self.matchestoxml(prefix="  ")
        s += "\n</%s>" % self.get_name()
	return s
