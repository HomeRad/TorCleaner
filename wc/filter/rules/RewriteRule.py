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

from UrlRule import UrlRule
from wc.XmlUtils import xmlify, unxmlify
from wc.log import *
from wc import i18n

# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
# tag part ids
TAG = 0
TAGNAME = 1
ATTR = 2
ATTRVAL = 3
COMPLETE = 4
ENCLOSED = 5
# a list
partvalnames = [
    'tag',
    'tagname',
    'attr',
    'attrval',
    'complete',
    'enclosed',
]
partnames = {
    'tag': i18n._("Tag"),
    'tagname': i18n._("Tag name"),
    'attr': i18n._("Attribute"),
    'attrval': i18n._("Attribute value"),
    'complete': i18n._("Complete tag"),
    'enclosed': i18n._("Enclosed block"),
}


# tags where close tag is missing
# note that this means that if the ending tag is there, it will not
# be filtered...
NO_CLOSE_TAGS = ('img', 'image', 'meta', 'br', 'link', 'area')


def part_num (s):
    """translation: tag name ==> tag number"""
    for i, part in enumerate(partvalnames):
        if part==s:
            return i
    return None


def num_part (i):
    """translation: tag number ==> tag name"""
    return partvalnames[i]


class RewriteRule (UrlRule):
    """A rewrite rule applies to a specific tag, optional with attribute
       constraints (stored in self.attrs) or a regular expression to
       match the enclosed block (self.enclosed).
    """
    def __init__ (self, sid=None, title="No title", desc="",
                  disable=0, tag="a", attrs=None, enclosed="", part=COMPLETE,
                  replacement=""):
        super(RewriteRule, self).__init__(sid=sid, title=title,
                                          desc=desc, disable=disable)
        self.tag = tag
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        self.part = part
        self.replacement = replacement
        self.enclosed = enclosed
        if self.enclosed and self.tag in NO_CLOSE_TAGS:
            raise ValueError("reading rule %s: tag %s has no end tag, so specifying an enclose value is invalid." % (`self.title`, `tag`))
        self.attrnames.append('tag')


    def fill_attrs (self, attrs, name):
        if name=='rewrite':
            super(RewriteRule, self).fill_attrs(attrs, name)
        elif name=='attr':
            val = unxmlify(attrs.get('name', 'href')).encode('iso8859-1')
            self.current_attr = val
            self.attrs[self.current_attr] = ""
        elif name=='replacement' and attrs.has_key('part'):
            self.part = part_num(unxmlify(attrs['part']).encode('iso8859-1'))


    def fill_data (self, data, name):
        if name=='attr':
            self.attrs[self.current_attr] += data
        elif name=='enclosed':
            self.enclosed += data
        elif name=='replacement':
            self.replacement += data


    def compile_data (self):
        super(RewriteRule, self).compile_data()
        self.enclosed = unxmlify(self.enclosed).encode('iso8859-1')
        self.replacement = unxmlify(self.replacement).encode('iso8859-1')
        for attr, val in self.attrs.items():
            self.attrs[attr] = unxmlify(val).encode('iso8859-1')
        self.set_start_sufficient()


    def fromFactory (self, factory):
        return factory.fromRewriteRule(self)


    def update (self, rule, dryrun=False, log=None):
        chg = super(RewriteRule, self).update(rule, dryrun=dryrun, log=log)
        attrs = ['attrs', 'part', 'replacement', 'enclosed']
        return self.update_attrs(attrs, rule, dryrun, log) or chg


    def _compute_start_sufficient (self):
        if self.tag in NO_CLOSE_TAGS:
            return True
        return self.part not in [ENCLOSED, COMPLETE, TAG, TAGNAME]


    def set_start_sufficient (self):
        self.start_sufficient = self._compute_start_sufficient()


    def match_tag (self, tag):
        return self.tag == tag


    def match_attrs (self, attrs):
        occurred = []
        for attr,val in attrs.items():
            # attr or val could be None
            if attr is None: attr = ''
            if val is None: val = ''
            occurred.append(attr)
            ro = self.attrs_ro.get(attr)
            if ro and not ro.search(val):
                return False
        for attr in self.attrs.keys():
            if attr not in occurred:
                return False
        return True


    def match_complete (self, pos, buf):
        """We know that the tag (and tag attributes) match. Now match
	   the enclosing block."""
        if not self.enclosed:
            # no enclosed expression => match
            return True
        # check every data for a match
        # remember that data is _not_ splitted across multiple items
        for n in buf[pos:]:
            if n[0]==DATA and self.enclosed_ro.search(n[1]):
                return True
        return False


    def filter_tag (self, tag, attrs):
        #debug(FILTER, "rule %s filter_tag", self.title)
        #debug(FILTER, "original tag %s attrs %s", `tag`, attrs)
        #debug(FILTER, "replace %s with %s", num_part(self.part), `self.replacement`)
        if self.part==COMPLETE:
            return [DATA, ""]
        if self.part==TAGNAME:
            return [STARTTAG, self.replacement, attrs]
        if self.part==TAG:
            return [DATA, self.replacement]
        if self.part==ENCLOSED:
            return [STARTTAG, tag, attrs]
        newattrs = {}
        # look for matching tag attributes
        for attr,val in attrs.items():
            ro = self.attrs_ro.get(attr)
            if ro:
                mo = ro.search(val)
                if mo:
                    if self.part==ATTR:
                        # replace complete attr, and make it possible
                        # for replacement to generate multiple attributes,
                        # eg "a=b c=d"
                        # XXX split does not honor quotes
                        for f in self.replacement.split():
                            if '=' in self.replacement:
                                k,v = f.split('=')
                                newattrs[k] = v
                            else:
                                newattrs[self.replacement] = None
                    elif self.part==ATTRVAL:
                        # backreferences are replaced
                        newattrs[attr] = mo.expand(self.replacement)
                    else:
                        error(FILTER, "Invalid part value %s" % str(self.part))
                    continue
            # nothing matched, just append the attribute as is
            newattrs[attr] = val
        #debug(FILTER, "filtered tag %s attrs %s", tag, newattrs)
        return [STARTTAG, tag, newattrs]


    def filter_complete (self, i, buf):
        #debug(FILTER, "rule %s filter_complete", self.title)
        #debug(FILTER, "original buffer %s", `buf`)
        #debug(FILTER, "part %s", num_part(self.part))
        if self.part==COMPLETE:
            buf[i:] = [[DATA, self.replacement]]
        elif self.part==TAG:
            buf[i] = [DATA, self.replacement]
            buf[-1] = [DATA, self.replacement]
        elif self.part==TAGNAME:
            buf[i] = [STARTTAG, self.replacement, {}]
            buf[-1] = [ENDTAG, self.replacement]
        elif self.part==ENCLOSED:
            buf[i+1:-1] = [[DATA, self.replacement]]
        #debug(FILTER, "filtered buffer %s", `buf`)


    def toxml (self):
        s = super(RewriteRule, self).toxml()
        if self.tag!='a':
            s += '\n tag="%s"' % self.tag
        if not (self.attrs or self.part!=COMPLETE or self.replacement or \
                self.enclosed):
            return s+"/>\n"
        s += ">\n"
        for key, val in self.attrs.items():
            s += "<attr"
            if key!='href':
                s += ' name="%s"' % key
            if val:
                s += ">"+xmlify(val)+"</attr>\n"
            else:
                s += "/>\n"
        if self.enclosed:
            s += "<enclosed>"+xmlify(self.enclosed)+"</enclosed>\n"
        s += "<replacement"
        s += ' part="%s"' % num_part(self.part)
        if self.replacement:
            s += '>'+xmlify(self.replacement)+"</replacement>\n"
        else:
            s += "/>\n"
        return s + "</rewrite>"


    def __str__ (self):
        s = super(RewriteRule, self).__str__()
        s += "tag %s\n" % self.tag
        for key,val in self.attrs.items():
            s += "attr: %s, %s\n" % (key,`val`)
        s += "enclosed %s\n" % `self.enclosed`
        s += "part %s\n" % num_part(self.part)
        s += "replacement %s\n" % `self.replacement`
        s += "start suff. %d" % self.start_sufficient
        return s
