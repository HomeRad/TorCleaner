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

import re
import wc.i18n
import wc
import wc.XmlUtils
import wc.filter.rules


def compileRegex (obj, attr):
    """regex-compile object attribute into <attr>_ro"""
    if hasattr(obj, attr) and getattr(obj, attr):
        setattr(obj, attr+"_ro", re.compile(getattr(obj, attr)))


class LangDict (dict):
    """Dictionary with a fallback algorithm, getting a default key entry if
       the requested key is not already mapped. Keys are usually languages
       like 'en' or 'de'."""

    def __getitem__ (self, key):
        """accessing an entry with unknown translation returns the default
           translated entry or if not found a random one or if the dict
           is empty an empty string"""
        if not self.has_key(key):
            # default is english
            if 'en' in self:
                return self['en']
            for val in self.itervalues():
                return val
            self[key] = ""
        return super(LangDict, self).__getitem__(key)


class Rule (object):
    """Basic rule class for filtering.
       After loading from XML (and having called compile_data), a rule has:
       titles - mapping of {lang -> translated titles}
       descriptions - mapping of {lang -> translated description}
        - sid - identification string (unique among all rules)
        - oid - dynamic sorting number (unique only for sorting in one level)
        - disable - flag to disable this rule
        - urlre - regular expression that matches urls applicable for this
          rule. leave empty to apply to all urls.
        - parent - the parent folder (if any); look at FolderRule class
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

    def _reset_parsed_data (self):
        """reset parsed rule data"""
        self._data = ""
        self._lang = "en"

    def update (self, rule, dryrun=False, log=None):
        """update title and description with given rule data"""
        assert self.sid == rule.sid, "updating %s with invalid rule %s" % \
                                     (self, rule)
        assert self.sid.startswith('wc'), "updating invalid id %s" % self.sid
        l = [a for a in self.attrnames if a not in ['sid', 'disable'] ]
        chg = self.update_attrs(l, rule, dryrun, log)
        chg = self.update_titledesc(rule, dryrun, log) or chg
        return chg

    def update_titledesc (self, rule, dryrun, log):
        """update rule title and description with given rule data"""
        chg = False
        for key, value in rule.titles.items():
            if not self.titles.has_key(key):
                oldvalue = ""
            elif self.titles[key]!=value:
                oldvalue = self.titles[key]
            else:
                oldvalue = None
            if oldvalue is not None:
                chg = True
                print >> log, " ", wc.i18n._("updating rule title for " \
                                            "language %s:") % key
                print >> log, " ", repr(oldvalue), "==>", repr(value)
                if not dryrun:
                    self.titles[key] = value
        for key, value in rule.descriptions.items():
            if not self.descriptions.has_key(key):
                oldvalue = ""
            elif self.descriptions[key]!=value:
                oldvalue = self.descriptions[key]
            else:
                oldvalue = None
            if oldvalue is not None:
                chg = True
                print >> log, " ", wc.i18n._("updating rule description for" \
                                             " language %s:") % key
                print >> log, " ", repr(oldvalue), "==>", repr(value)
                if not dryrun:
                    self.descriptions[key] = value
        return chg

    def update_attrs (self, attrs, rule, dryrun, log):
        """update rule attributes (specified by attrs) with given rule data"""
        chg = False
        for attr in attrs:
            oldval = getattr(self, attr)
            newval = getattr(rule, attr)
            if oldval != newval:
                print >> log, " ", \
                         wc.i18n._("updating rule %s:") % self.tiptext()
                print >> log, " ", attr, repr(oldval), "==>", repr(newval)
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
        self._reset_parsed_data()
        if name in ('title', 'description'):
            self._lang = attrs['lang']
            return
        for attr in self.attrnames:
            if attrs.has_key(attr):
                setattr(self, attr, attrs[attr])
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
        if name == self.get_name():
            self._data = ""
        else:
            self._data = wc.XmlUtils.xmlunquote(self._data)
        if name == 'title':
            self.titles[self._lang] = self._data
        elif name == 'description':
            self.descriptions[self._lang] = self._data

    def compile_data (self):
        """register this rule; called when all XML parsing of rule finished"""
        wc.filter.rules.register_rule(self)

    def get_name (self):
        """class name without "Rule" suffix, in lowercase"""
        return self.__class__.__name__[:-4].lower()

    def toxml (self):
        """Rule data as XML for storing, must be overridden in subclass"""
        s = u'<%s sid="%s"' % (self.get_name(),
                               wc.XmlUtils.xmlquoteattr(self.sid))
        if self.disable:
            s += u' disable="%d"' % self.disable
        return s

    def title_desc_toxml (self, prefix=""):
        """return XML for rule title and description"""
        t = [u'%s<title lang="%s">%s</title>' % \
             (prefix, wc.XmlUtils.xmlquoteattr(key),
              wc.XmlUtils.xmlquote(value)) \
             for key,value in self.titles.iteritems() if value]
        d = [u'%s<description lang="%s">%s</description>' % \
             (prefix, wc.XmlUtils.xmlquoteattr(key),
              wc.XmlUtils.xmlquote(value)) \
             for key,value in self.descriptions.iteritems() if value]
        return u"\n".join(t+d)

    def __str__ (self):
        """return basic rule data as string"""
        s = self.get_name()+"\n"
        if self.sid is not None:
            s += "sid     %s\n" % self.sid.encode("iso-8859-1")
        s += "disable %d\n" % self.disable
        s += "title %s\n" % self.titles['en'].encode("iso-8859-1")
        return s

    def tiptext (self):
        """return short info for gui display"""
        return u"%s #%s" % (self.get_name().capitalize(), self.sid)
