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

from AllowRule import AllowRule
from Rule import Rule
from wc.XmlUtils import xmlify, unxmlify

class BlockRule (AllowRule):
    def __init__ (self, title="No title", desc="", disable=0, scheme="",
                  host="", port="", path="", parameters="", query="",
		  fragment="", url="", oid=0):
        super(BlockRule, self).__init__(title=title, desc=desc, disable=disable,
                           scheme=scheme, host=host, port=port, path=path,
                           parameters=parameters, query=query,
                           fragment=fragment, oid=oid)
        self.url = url


    def fill_data (self, data, name):
        if name=='block':
            self.url += unxmlify(data).encode('iso8859-1')


    def fromFactory (self, factory):
        return factory.fromBlockRule(self)


    def toxml (self):
        # chop off the last two chars '/>'
        s = super(BlockRule, self).toxml()[:-2]
        if self.url:
            return s+">"+xmlify(self.url)+"</block>"
        return s+"/>"
