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

from UrlRule import UrlRule

class NocommentsRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)

    def fromFactory (self, factory):
        return factory.fromNocommentsRule(self)

    def toxml (self):
	return UrlRule.toxml(self) + "/>"

