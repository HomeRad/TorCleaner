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

from Rule import Rule
from wc import i18n

def recalc_oids (rules):
    for i, rule in enumerate(rules):
        rule.oid = i

def recalc_up_down (rules):
    upper = len(rules)-1
    for i, rule in enumerate(rules):
        rule.up = (i>0)
        rule.down = (i<upper)


class FolderRule (Rule):
    def __init__ (self, sid=None, oid=None, title="No title", desc="",
                  disable=0, lang="", filename=""):
        super(FolderRule, self).__init__(sid=sid, oid=oid, title=title,
                                         desc=desc, disable=disable)
        # make filename read-only
        self.__filename = filename
        self.lang = lang
        self.rules = []


    def __str__ (self):
        return super(FolderRule, self).__str__()+ \
            ("\nrules:   %d"%len(self.rules))+ \
            ("\nlang:    %s"%self.lang)


    def filename_get (self):
        return self.__filename
    filename = property(filename_get)


    def fromFactory (self, factory):
        return factory.fromFolderRule(self)


    def append_rule (self, r):
        self.rules.append(r)
        r.parent = self
        # sort to recalculate rule oids
        self.sort()


    def delete_rule (self, i):
        r = self.rules[i]
        del self.rules[i]


    def sort (self):
        self.rules.sort()
        recalc_oids(self.rules)
        recalc_up_down(self.rules)


    def toxml (self):
        s = """<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
%s""" % super(FolderRule, self).toxml()
        if self.lang:
            s += '\n lang="%s"' % self.lang
        s += ">\n"
        for r in self.rules:
            s += "\n%s\n"%r.toxml()
        return s+"</folder>\n"


    def tiptext (self):
        """return short info for gui display"""
        l = len(self.rules)
        if l==1:
            text = i18n._("%d rule")%l
        else:
            text = i18n._("%d rules")%l
        return "%s, %s" % (super(FolderRule, self).tiptext(), text)

