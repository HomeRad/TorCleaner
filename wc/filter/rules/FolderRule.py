# -*- coding: iso-8859-1 -*-
"""group filter rules into folders"""
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

from Rule import Rule
from wc import i18n, ConfigCharset

# for display up/down arrows in GUIs
def recalc_up_down (rules):
    upper = len(rules)-1
    for i, rule in enumerate(rules):
        rule.up = (i>0)
        rule.down = (i<upper)


class FolderRule (Rule):
    def __init__ (self, sid=None, title="No title", desc="",
                  disable=0, filename=""):
        super(FolderRule, self).__init__(sid=sid, title=title,
                                         desc=desc, disable=disable)
        # make filename read-only
        self._filename = filename
        self.rules = []
        self.attrnames.append('oid')
        self.intattrs.append('oid')
        self.oid = None


    def __str__ (self):
        return super(FolderRule, self).__str__()+ \
            ("\nrules:   %d"%len(self.rules))


    def filename_get (self):
        return self._filename
    filename = property(filename_get)


    def fromFactory (self, factory):
        return factory.fromFolderRule(self)


    def append_rule (self, r):
        r.oid = len(self.rules)
        # note: the rules are added in order
        self.rules.append(r)
        r.parent = self


    def delete_rule (self, i):
        del self.rules[i]
        recalc_up_down(self.rules)


    def update (self, folder, dryrun=False, log=None):
        """update this folder with given folder data"""
        chg = super(FolderRule, self).update(folder, dryrun=dryrun, log=log)
        for rule in folder.rules:
            if not rule.sid.startswith("wc"):
                # ignore local rules
                continue
            oldrule = self.get_rule(rule.sid)
            if oldrule is not None:
                chg = oldrule.update(rule, dryrun=dryrun, log=log) or chg
            else:
                print >>log, i18n._("inserting new rule %s")%rule.tiptext()
                if not dryrun:
                    self.rules.append(rule)
                    chg = True
        if chg:
            recalc_up_down(self.rules)
        return chg


    def get_rule (self, sid):
        """return rule with given sid or None if not found"""
        for rule in self.rules:
            if rule.sid==sid:
                return rule
        return None


    def toxml (self):
        s = """<?xml version="1.0" encoding="%s"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
%s oid="%d">""" % (ConfigCharset, super(FolderRule, self).toxml(), self.oid)
        for r in self.rules:
            s += "\n%s\n"%r.toxml()
        return s+"</folder>\n"


    def write (self):
        f = file(self.filename, 'w')
        f.write(self.toxml())
        f.close()


    def tiptext (self):
        """return short info for gui display"""
        l = len(self.rules)
        if l==1:
            text = i18n._("with 1 rule")
        else:
            text = i18n._("with %d rules")%l
        return "%s %s" % (super(FolderRule, self).tiptext(), text)
