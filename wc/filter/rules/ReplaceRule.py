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

class ReplaceRule (UrlRule):
    def __init__ (self, sid=None, oid=None, title="No title", desc="",
                  disable=0, search="", replace=""):
        super(ReplaceRule, self).__init__(sid=sid, oid=oid, title=title,
                                          desc=desc, disable=disable)
        self.search = search
        self.replace = replace
        self.attrnames.append('search')


    def fill_data (self, data, name):
        if name=='replacer':
            self.replace += unxmlify(data).encode('iso8859-1')


    def fromFactory (self, factory):
        return factory.fromReplaceRule(self)


    def update (self, rule, dryrun=False, log=None):
        super(ReplaceRule, self).update(rule, dryrun=dryrun, log=log)
        self.update_attrs(['replace'], rule, dryrun, log)


    def toxml (self):
	s = super(ReplaceRule, self).toxml()
        if self.search:
            s += '\n search="%s"'%xmlify(self.search)
        if self.replace:
            return s+">"+xmlify(self.replace)+"</replacer>"
        return s+"/>"
