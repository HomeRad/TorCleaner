# -*- coding: iso-8859-1 -*-
"""hold a list of urls/domains to filter in external files, like those
found in SquidGuard"""
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

import wc.filter.rules.Rule
import wc.XmlUtils

class ExternfileRule (wc.filter.rules.Rule.Rule):
    """rule with data stored in a (compressed) external file, used for
       huge url and domain block lists
    """
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, filename=None):
        """initialize rule attributes"""
        super(ExternfileRule, self).__init__(sid=sid, titles=titles,
                                  descriptions=descriptions, disable=disable)
        self.filename = filename
        self.attrnames.append('filename')


    def __str__ (self):
        """return rule data as string"""
        return "%sfile %s\n" % \
            (super(ExternfileRule, self).__str__(), repr(self.filename))


    def toxml (self):
        """Rule data as XML for storing"""
        s = super(ExternfileRule, self).toxml()
        s += ' filename="%s">' % wc.XmlUtils.xmlquoteattr(self.filename)
        s += "\n"+self.title_desc_toxml(prefix="  ")
        s += "\n</%s>"%self.get_name()
        return s
