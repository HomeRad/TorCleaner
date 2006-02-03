# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
"""
Basic rule class and routines.
"""

import re
import wc
import wc.XmlUtils
import wc.filter.rules


def compileRegex (obj, attr, fullmatch=False, flags=0):
    """
    Regex-compile object attribute into <attr>_ro.
    """
    if hasattr(obj, attr):
        val = getattr(obj, attr)
        if val:
            if fullmatch:
                val = "^(%s)$" % val
            setattr(obj, attr+"_ro", re.compile(val, flags))


class LangDict (dict):
    """
    Dictionary with a fallback algorithm, getting a default key entry if
    the requested key is not already mapped. Keys are usually languages
    like 'en' or 'de'.
    """

    def __getitem__ (self, key):
        """
        Accessing an entry with unknown translation returns the default
        translated entry or if not found a random one or if the dict
        is empty an empty string.
        """
        if not self.has_key(key):
            # default is english
            if 'en' in self:
                return self['en']
            for val in self.itervalues():
                return val
            self[key] = ""
        return super(LangDict, self).__getitem__(key)


class Rule (object):
    """
    Basic rule class for filtering.

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

    # Attributes that cannot be used for custom data.
    reserved_attrnames = [
        'sid', 'name', 'titles', 'descriptions', 'disable', 'parent',
        'attrnames', 'intattrs', 'listattrs',
    ]

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, parent=None):
        """
        Initialize basic rule data.
        """
        self.sid = sid
        # class name without "Rule" suffix, in lowercase
        self.name = self.__class__.__name__[:-4].lower()
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
        """
        Reset parsed rule data.
        """
        self._data = u""
        self._lang = u"en"

    def update (self, rule, dryrun=False, log=None):
        """
        Update title and description with given rule data.
        """
        assert self.sid == rule.sid, "updating %s with invalid rule %s" % \
                                     (self, rule)
        assert self.sid.startswith('wc'), "updating invalid id %s" % self.sid
        l = [a for a in self.attrnames if a not in self.reserved_attrnames]
        chg = self.update_attrs(l, rule, dryrun, log)
        chg = self.update_titledesc(rule, dryrun, log) or chg
        return chg

    def update_titledesc (self, rule, dryrun, log):
        """
        Update rule title and description with given rule data.
        """
        chg = False
        for key, value in rule.titles.iteritems():
            if not self.titles.has_key(key):
                oldvalue = ""
            elif self.titles[key] != value:
                oldvalue = self.titles[key]
            else:
                oldvalue = None
            if oldvalue is not None:
                chg = True
                print >> log, " ", _("updating rule title for " \
                                            "language %s:") % key
                print >> log, " ", repr(oldvalue), "==>", repr(value)
                if not dryrun:
                    self.titles[key] = value
        for key, value in rule.descriptions.iteritems():
            if not self.descriptions.has_key(key):
                oldvalue = ""
            elif self.descriptions[key] != value:
                oldvalue = self.descriptions[key]
            else:
                oldvalue = None
            if oldvalue is not None:
                chg = True
                print >> log, " ", _("updating rule description for" \
                                             " language %s:") % key
                print >> log, " ", repr(oldvalue), "==>", repr(value)
                if not dryrun:
                    self.descriptions[key] = value
        return chg

    def update_attrs (self, attrs, rule, dryrun, log):
        """
        Update rule attributes (specified by attrs) with given rule data.
        """
        chg = False
        for attr in attrs:
            oldval = getattr(self, attr)
            newval = getattr(rule, attr)
            if oldval != newval:
                print >> log, " ", \
                         _("updating rule %s:") % self.tiptext()
                print >> log, " ", attr, repr(oldval), "==>", repr(newval)
                chg = True
                if not dryrun:
                    setattr(self, attr, newval)
        return chg

    def __lt__ (self, other):
        """
        True iff self < other according to oid.
        """
        return self.oid < other.oid

    def __le__ (self, other):
        """
        True iff self <= other according to oid.
        """
        return self.oid <= other.oid

    def __eq__ (self, other):
        """
        True iff self == other according to oid.
        """
        return self.oid == other.oid

    def __ne__ (self, other):
        """
        True iff self != other according to oid.
        """
        return self.oid != other.oid

    def __gt__ (self, other):
        """
        True iff self > other according to oid.
        """
        return self.oid > other.oid

    def __ge__ (self, other):
        """
        True iff self >= other according to oid.
        """
        return self.oid >= other.oid

    def __hash__ (self):
        """
        Hash value.
        """
        return self.sid

    def fill_attrs (self, attrs, name):
        """
        Initialize rule attributes with given attrs.
        """
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
        """
        Called when XML character data was parsed to fill rule values.
        """
        self._data += data

    def end_data (self, name):
        """
        Called when XML end element was reached.
        """
        if name == self.name:
            self._data = u""
        else:
            self._data = wc.XmlUtils.xmlunquote(self._data)
        if name == 'title':
            self.titles[self._lang] = self._data
        elif name == 'description':
            self.descriptions[self._lang] = self._data

    def compile_data (self):
        """
        Register this rule. Called when all XML parsing of rule is finished.
        """
        wc.filter.rules.register_rule(self)
        # some internal checks
        for name in self.intattrs:
            assert name in self.attrnames
        for name in self.listattrs:
            assert name in self.attrnames
        for name in self.attrnames:
            if name not in ('sid', 'disable'):
                assert name not in self.reserved_attrnames

    def toxml (self):
        """
        Rule data as XML for storing, must be overridden in subclass.
        """
        s = u'<%s sid="%s"' % (self.name, wc.XmlUtils.xmlquoteattr(self.sid))
        if self.disable:
            s += u' disable="%d"' % self.disable
        return s

    def title_desc_toxml (self, prefix=""):
        """
        XML for rule title and description.
        """
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
        """
        Basic rule data as ISO-8859-1 encoded string.
        """
        s = "Rule %s\n" % self.name
        if self.sid is not None:
            s += "sid     %s\n" % self.sid.encode("iso-8859-1")
        s += "disable %d\n" % self.disable
        s += "title %s\n" % self.titles['en'].encode("iso-8859-1")
        return s

    def tiptext (self):
        """
        Short info for gui display.
        """
        return u"%s #%s" % (self.name.capitalize(), self.sid)

    def applies_to_url (self, url):
        """
        Wether rule applies to given URL.
        """
        return True

    def applies_to_mime (self, mime):
        """
        Wether rule applies to given MIME type.
        """
        return True
