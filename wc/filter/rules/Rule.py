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

import wc, wc.filter.rules
from wc.XmlUtils import xmlify, unxmlify
from types import IntType


class Rule (object):
    """Basic rule class for filtering.
    A basic rule has:
       title - the title
       sid - identification string (unique among all sid)
       oid - sorting number (unique only for sorting in one level)
       desc - the description
       disable - flag to disable this rule
       urlre - regular expression that matches urls applicable for this rule.
               leave empty to apply to all urls.
       parent - the parent folder (if any); look at FolderRule class
    """
    def __init__ (self, sid=None, oid=None, title="<title>", desc="",
                  disable=0, parent=None):
        self.sid = sid
        self.title = title
        if oid is None:
            self.oid = wc.filter.rules.oidcounter
            wc.filter.rules.oidcounter += 1
        else:
            self.oid = oid
	    if oid >= wc.filter.rules.oidcounter:
	        wc.filter.rules.oidcounter = oid+1
        self.desc = desc
        self.disable = disable
        self.parent = parent
        self.attrnames = ['title', 'desc', 'disable', 'sid', 'oid']
        self.intattrs = ['disable', 'oid']
        self.listattrs = []


    def update (self, rule, dryrun=False, log=None):
        """update title and description with given rule data"""
        assert self.sid==rule.sid, "updating %s with invalid rule %s" % \
                (str(self), str(rule))
        assert self.sid.startswith('wc'), "updating invalid id %s" % self.sid
        print >>log, "updating rule", self.tiptext()
        l = [a for a in self.attrnames if a not in ['sid', 'oid', 'disable'] ]
        self.update_attrs(l, rule, dryrun, log)


    def update_attrs (self, attrs, rule, dryrun, log):
        for attr in attrs:
            oldval = getattr(self, attr)
            newval = getattr(rule, attr)
            if oldval != newval:
                print >>log, attr, `oldval`, "==>", `newval`
                if not dryrun:
                    setattr(self, attr, newval)


    def __lt__ (self, other):
        return self.oid < other.oid


    def __le__ (self, other):
        return self.oid <= other.oid


    def __eq__ (self, other):
        return self.oid == other.oid


    def __ne__ (self, other):
        return self.oid != other.oid


    def __gt__ (self, other):
        return self.oid > other.oid


    def __ge__ (self, other):
        return self.oid >= other.oid


    def __hash__ (self):
        return self.oid


    def fill_attrs (self, attrs, name):
        for attr in self.attrnames:
            if attrs.has_key(attr):
                val = unxmlify(attrs[attr])
                setattr(self, attr, val)
        for attr in self.intattrs:
            val = getattr(self, attr)
            if val:
                setattr(self, attr, int(val))
            else:
                setattr(self, attr, 0)
        for attr in self.listattrs:
            val = getattr(self, attr)
            if val:
                setattr(self, attr, val.split(","))
            else:
                setattr(self, attr, [])


    def fill_data (self, data, name):
        pass


    def fromFactory (self, factory):
        return factory.fromRule(self)


    def get_name (self):
        """class name without "Rule" suffix, in lowercase"""
        return self.__class__.__name__[:-4].lower()


    def toxml (self):
        s = "<"+self.get_name()
        s += ' sid="%s"' % xmlify(self.sid)
	s += ' oid="%d"' % self.oid
        s += ' title="%s"' % xmlify(self.title)
        if self.desc:
            s += '\n desc="%s"' % xmlify(self.desc)
        if self.disable:
            s += '\n disable="1"'
        return s


    def __str__ (self):
        s = self.get_name()+"\n"
        s += "sid     %s\n" % self.sid
        s += "title   %s\n" % `self.title`
	s += "oid     %d\n" % self.oid
        s += "desc    %s\n" % `self.desc`
        s += "disable %d\n" % self.disable
        return s


    def tiptext (self):
        """return short info for gui display"""
        return "%s #%s" % (self.get_name().capitalize(), self.sid)

