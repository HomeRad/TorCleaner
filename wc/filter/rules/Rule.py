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
       oid - identification number, also used for sorting
       desc - the description
       disable - flag to disable this rule
       urlre - regular expression that matches urls applicable for this rule.
               leave empty to apply to all urls.
       parent - the parent folder (if any); look at FolderRule class
    """
    def __init__ (self, title="No title", desc="", disable=0, parent=None,
                  oid=0):
        self.title = title
        if not oid:
            self.oid = wc.filter.rules.rulecounter
            wc.filter.rules.rulecounter += 1
        else:
            self.oid = oid
	    if oid >= wc.filter.rules.rulecounter:
	        wc.filter.rules.rulecounter = oid+1
        self.desc = desc
        self.disable = disable
        self.parent = parent
        self.attrnames = ['title', 'desc', 'disable', 'oid']
        self.intattrs = ['disable', 'oid']
        self.listattrs = []


    def __cmp__ (self, other):
        return cmp(self.oid, other.oid)


    def fill_attrs (self, attrs, name):
        for attr in self.attrnames:
            if attrs.has_key(attr):
                val = unxmlify(attrs[attr]).encode('iso8859-1')
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
        s += ' title="%s"' % xmlify(self.title)
	s += ' oid="%d"' % self.oid
        if self.desc:
            s += '\n desc="%s"' % xmlify(self.desc)
        if self.disable:
            s += '\n disable="1"'
        return s


    def __str__ (self):
        s = self.get_name()+"\n"
        s += "title   %s\n" % `self.title`
	s += "oid     %d\n" % self.oid
        s += "desc    %s\n" % `self.desc`
        s += "disable %d\n" % self.disable
        return s


    def tiptext (self):
        """return short info for gui display"""
        return "%s #%d" % (self.get_name().capitalize(), self.oid)
