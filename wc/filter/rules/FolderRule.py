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

import bk.i18n
import wc
import wc.filter.rules.Rule


def recalc_up_down (rules):
    """add .up and .down attributes to rules, used for display up/down
       arrows in GUIs
    """
    upper = len(rules)-1
    for i, rule in enumerate(rules):
        rule.up = (i>0)
        rule.down = (i<upper)


class FolderRule (wc.filter.rules.Rule.Rule):
    """container for a list of rules"""

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, filename=""):
        """initialize rule data"""
        super(FolderRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        # make filename read-only
        self._filename = filename
        self.rules = []
        self.attrnames.append('oid')
        self.intattrs.append('oid')
        self.oid = None

    def __str__ (self):
        """return rule data as string"""
        return super(FolderRule, self).__str__()+ \
            ("\nrules:   %d"%len(self.rules))

    def filename_get (self):
        """get filename where this folder is stored"""
        return self._filename
    filename = property(filename_get)


    def append_rule (self, r):
        """append rule to folder"""
        r.oid = len(self.rules)
        # note: the rules are added in order
        self.rules.append(r)
        r.parent = self

    def delete_rule (self, i):
        """delete rule from folder with index i"""
        del self.rules[i]
        recalc_up_down(self.rules)

    def update (self, rule, dryrun=False, log=None):
        """update this folder with given folder rule data"""
        chg = super(FolderRule, self).update(rule, dryrun=dryrun, log=log)
        for child in rule.rules:
            if not child.sid.startswith("wc"):
                # ignore local rules
                continue
            oldrule = self.get_rule(child.sid)
            if oldrule is not None:
                if oldrule.update(child, dryrun=dryrun, log=log):
                    chg = True
            else:
                print >>log, bk.i18n._("inserting new rule %s") % \
                             child.tiptext()
                if not dryrun:
                    self.rules.append(child)
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
        """Rule data as XML for storing"""
        s = u"""<?xml version="1.0" encoding="%s"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
%s oid="%d">"""%(wc.ConfigCharset, super(FolderRule, self).toxml(), self.oid)
        s += u"\n"+self.title_desc_toxml()+u"\n"
        for r in self.rules:
            s += u"\n%s\n"%r.toxml()
        return s+u"</folder>\n"


    def write (self):
        """write xml data into filename"""
        f = file(self.filename, 'w')
        f.write(self.toxml().encode("iso-8859-1", "replace"))
        f.close()


    def tiptext (self):
        """return short info for gui display"""
        l = len(self.rules)
        if l==1:
            text = bk.i18n._("with 1 rule")
        else:
            text = bk.i18n._("with %d rules")%l
        return "%s %s" % (super(FolderRule, self).tiptext(), text)
