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

from Rule import Rule

def recalc_oids (rules):
    i = 0
    for r in rules:
        r.oid = i
        i += 1

class FolderRule (Rule):
    def __init__ (self, title="No title", desc="", disable=0, lang="",
                  filename="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.filename = filename
        self.lang = lang
        self.rules = []

    def fromFactory (self, factory):
        return factory.fromFolderRule(self)

    def append_rule (self, r):
        self.rules.append(r)
        r.parent = self

    def delete_rule (self, i):
        r = self.rules[i]
        del self.rules[i]

    def sort (self):
        self.rules.sort()
        recalc_oids(self.rules)

    def toxml (self):
        s = """<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
""" + Rule.toxml(self)
        if self.lang:
            s += '\n lang="%s"' % self.lang
        s += ">\n"
        for r in self.rules:
            s += "\n%s\n"%r.toxml()
        return s+"</folder>\n"

