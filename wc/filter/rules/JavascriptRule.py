# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2008 Bastian Kleineidam
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
JavaScript filter rule.
"""
from . import UrlRule


class JavascriptRule (UrlRule.UrlRule):
    """
    If enabled, this rule tells the HtmlRewriter to filter JavaScript.
    """

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(JavascriptRule, self).toxml()
        s += self.endxml()
        return s
