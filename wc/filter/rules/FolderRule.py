# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Group filter rules into folders.
"""
from ... import fileutil, configuration
from . import Rule


def recalc_up_down(rules):
    """
    Add .up and .down attributes to rules, used for display up/down
    arrows in GUIs
    """
    upper = len(rules)-1
    for i, rule in enumerate(rules):
        rule.up = (i>0)
        rule.down = (i<upper)


class FolderRule(Rule.Rule):
    """
    Container for a list of rules.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, filename=""):
        """
        Initialize rule data.
        """
        super(FolderRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        # make filename read-only
        self._filename = filename
        self.rules = []
        self.attrnames.extend(('oid', 'configversion'))
        self.intattrs.append('oid')
        self.oid = None
        self.configversion = "-"

    def __str__(self):
        """
        Return rule data as string.
        """
        return super(FolderRule, self).__str__() + \
            ("\nrules:   %d" % len(self.rules))

    def filename_get(self):
        """
        Get filename where this folder is stored.
        """
        return self._filename
    filename = property(filename_get)

    def append_rule(self, r):
        """
        Append rule to folder.
        """
        r.oid = len(self.rules)
        # note: the rules are added in order
        self.rules.append(r)
        r.parent = self

    def delete_rule(self, i):
        """
        Delete rule from folder with index i.
        """
        del self.rules[i]
        recalc_up_down(self.rules)

    def update(self, rule, dryrun=False, log=None):
        """
        Update this folder with given folder rule data.
        """
        chg = super(FolderRule, self).update(rule, dryrun=dryrun, log=log)
        for child in rule.rules:
            if child.sid is None or not child.sid.startswith("wc"):
                # ignore local rules
                continue
            oldrule = self.get_rule(child.sid)
            if oldrule is not None:
                if oldrule.update(child, dryrun=dryrun, log=log):
                    chg = True
            else:
                print >> log, _("inserting new rule %s") % \
                             child.tiptext()
                if not dryrun:
                    self.rules.append(child)
                    chg = True
        if chg:
            recalc_up_down(self.rules)
        return chg

    def get_rule(self, sid):
        """
        Return rule with given sid or None if not found.
        """
        for rule in self.rules:
            if rule.sid == sid:
                return rule
        return None

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = u"""<?xml version="1.0" encoding="%s"?>
<!DOCTYPE folder SYSTEM "filter.dtd">
%s oid="%d" configversion="%s">""" % \
      (configuration.ConfigCharset, super(FolderRule, self).toxml(),
       self.oid, self.configversion)
        s += u"\n"+self.title_desc_toxml()+u"\n"
        for r in self.rules:
            s += u"\n%s\n" % r.toxml()
        return s+u"</folder>\n"

    def write(self, fd=None):
        """
        Write xml data into filename.
        @raise: OSError if file could not be written.
        """
        s = self.toxml().encode("iso-8859-1", "replace")
        if fd is None:
            fileutil.write_file(self.filename, s)
        else:
            fd.write(s)

    def tiptext(self):
        """
        Return short info for gui display.
        """
        l = len(self.rules)
        if l == 1:
            text = _("with 1 rule")
        else:
            text = _("with %d rules") % l
        return "%s %s" % (super(FolderRule, self).tiptext(), text)
