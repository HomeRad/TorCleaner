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

from UrlRule import UrlRule
from wc import xmlify, unxmlify

class HeaderRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, name="",
                  value="", oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.name = name
        self.value = value
        self.attrnames.append('name')

    def fill_data (self, data, name):
        if name=='header':
            self.value = unxmlify(data).encode('iso8859-1')

    def fromFactory (self, factory):
        return factory.fromHeaderRule(self)

    def toxml (self):
        s = '%s\n name="%s"'%(UrlRule.toxml(self), xmlify(self.name))
        if self.value:
            return s+">"+xmlify(self.value)+"</header>"
        return s+"/>"

