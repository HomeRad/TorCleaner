# -*- coding: iso-8859-1 -*-
"""basic rule class and routines"""
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

import re
from wc import i18n
from wc.XmlUtils import xmlify, unxmlify
from wc.filter.rules import register_rule


# compile object attribute
def compileRegex (obj, attr):
    if hasattr(obj, attr) and getattr(obj, attr):
        setattr(obj, attr+"_ro", re.compile(getattr(obj, attr)))

class LangDict (dict):
    """accessing an entry with unknown translation returns the default
       translated entry or a random one"""
    def __getitem__ (self, key):
        if not self.has_key(key):
            assert self
            # default is english
            if 'en' in self:
                return self['en']
            for val in self.itervalues():
                return val
        return super(LangDict, self).__getitem__(key)


class Rule (object):
    """Basic rule class for filtering.
       After loading from XML (and having called compile_data), a rule has:
        titles - mapping of {lang -> translated titles}
        descriptions - mapping of {lang -> translated description}
        sid - identification string (unique among all rules)
        oid - dynamic sorting number (unique only for sorting in one level)
        disable - flag to disable this rule
        urlre - regular expression that matches urls applicable for this rule.
                leave empty to apply to all urls.
        parent - the parent folder (if any); look at FolderRule class
    """
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, parent=None):
        """initialize basic rule data"""
        self.sid = sid
        self.titles = LangDict()
        if titles is not None:
            self.titles.update(titles)
        self.descriptions = LangDict()
        if descriptions is not None:
            self.descriptions.update(descriptions)
        self.disable = disable
        self.parent = parent
        self.attrnames = ['disable', 'sid']
        self.intattrs = ['disable']
        self.listattrs = []
        self._reset_parsed_data()


    def _reset_parsed_data (self):
        self._data = ""
        self._lang = "en"


    def update (self, rule, dryrun=False, log=None):
        """update title and description with given rule data"""
        assert self.sid==rule.sid, "updating %s with invalid rule %s"%(self, rule)
        assert self.sid.startswith('wc'), "updating invalid id %s" % self.sid
        l = [a for a in self.attrnames if a not in ['sid', 'disable'] ]
        return self.update_attrs(l, rule, dryrun, log)


    def update_attrs (self, attrs, rule, dryrun, log):
        """update rule attributes (specified by attrs) with given rule data"""
        chg = False
        for attr in attrs:
            oldval = getattr(self, attr)
            newval = getattr(rule, attr)
            if oldval != newval:
                print >>log, " ", i18n._("updating rule %s:")%self.tiptext()
                print >>log, " ", attr, repr(oldval), "==>", repr(newval)
                chg = True
                if not dryrun:
                    setattr(self, attr, newval)
        return chg


    def __lt__ (self, other):
        """True iff self < other according to oid"""
        return self.oid < other.oid


    def __le__ (self, other):
        """True iff self <= other according to oid"""
        return self.oid <= other.oid


    def __eq__ (self, other):
        """True iff self == other according to oid"""
        return self.oid == other.oid


    def __ne__ (self, other):
        """True iff self != other according to oid"""
        return self.oid != other.oid


    def __gt__ (self, other):
        """True iff self > other according to oid"""
        return self.oid > other.oid


    def __ge__ (self, other):
        """True iff self >= other according to oid"""
        return self.oid >= other.oid


    def __hash__ (self):
        """return hash value"""
        return self.sid


    def fill_attrs (self, attrs, name):
        """initialize rule attributes with given attrs"""
        if name in ('title', 'description'):
            self._lang = attrs['lang']
            return
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
        """called when XML character data was parsed to fill rule values"""
        self._data += data


    def end_data (self, name):
        """called when XML end element was reached"""
        if name=='title':
            self.titles[self._lang] = unxmlify(self._data).encode('iso8859-1')
            self._reset_parsed_data()
        elif name=='description':
            self.descriptions[self._lang] = unxmlify(self._data).encode('iso8859-1')
            self._reset_parsed_data()


    def compile_data (self):
        """register this rule; called when all XML parsing of rule finished"""
        register_rule(self)


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromRule(self)


    def get_name (self):
        """class name without "Rule" suffix, in lowercase"""
        return self.__class__.__name__[:-4].lower()


    def toxml (self):
        """Rule data as XML for storing, must be overridden in subclass"""
        return '<%s sid="%s"' % (self.get_name(), xmlify(self.sid))


    def title_desc_toxml (self):
        t = ['<title lang="%s">%s</title>'%(xmlify(key), xmlify(value)) \
             for key,value in self.titles.iteritems()]
        d = ['<description lang="%s">%s</description>'% \
             (xmlify(key), xmlify(value)) \
             for key,value in self.descriptions.iteritems()]
        return "\n".join(t+d)


    def __str__ (self):
        """return basic rule data as string"""
        s = self.get_name()+"\n"
        s += "sid     %s\n" % self.sid
        s += "disable %d\n" % self.disable
        s += "title %s\n" % self.titles['en']
        return s


    def tiptext (self):
        """return short info for gui display"""
        return "%s #%s" % (self.get_name().capitalize(), self.sid)

