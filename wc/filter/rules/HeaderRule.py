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

from UrlRule import UrlRule
from wc.XmlUtils import xmlify, unxmlify

class HeaderRule (UrlRule):
    """rule for filtering HTTP headers"""

    def __init__ (self, sid=None, oid=None, title="No title", desc="",
                  disable=0, name="noname", value=""):
        """init rule name and value"""
        super(HeaderRule, self).__init__(sid=sid, oid=oid, title=title,
                                         desc=desc, disable=disable)
        self.name = name
        self.value = value
        self.attrnames.append('name')


    def fill_data (self, data, name):
        if name=='header':
            self.value = unxmlify(data).encode('iso8859-1')


    def fromFactory (self, factory):
        return factory.fromHeaderRule(self)


    def toxml (self):
        s = '%s\n name="%s"' % \
            (super(HeaderRule, self).toxml(), xmlify(self.name))
        if self.value:
            return s+">"+xmlify(self.value)+"</header>"
        return s+"/>"
