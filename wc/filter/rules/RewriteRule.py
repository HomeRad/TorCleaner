# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
Rule rewriting html tags.
"""

import re

import wc
import wc.log
import wc.XmlUtils
import wc.filter.rules.UrlRule
import wc.filter.rules.Rule
import wc.HtmlParser.htmllib
from wc.webgui import ZTUtils


# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
STARTENDTAG = 4
# tag part ids
TAG = 0
TAGNAME = 1
ATTR = 2
ATTRVAL = 3
COMPLETE = 4
ENCLOSED = 5

def _startout (out, item, end):
    """
    Write given item data on output stream as HTML start tag.
    """
    out.write(u"<")
    out.write(item[1])
    for name, val in item[2].items():
        out.write(u' %s' % name)
        if val:
            out.write(u'="%s"' % wc.HtmlParser.htmllib.quote_attrval(val))
    out.write(end)


def tagbuf2data (tagbuf, out):
    """
    Write tag buffer items to output stream out and returns out.
    """
    for item in tagbuf:
        if item[0] == DATA:
            out.write(item[1])
        elif item[0] == STARTTAG:
            _startout(out, item, u">")
        elif item[0] == ENDTAG:
            out.write(u"</%s>" % item[1])
        elif item[0] == COMMENT:
            out.write(u"<!--%s-->" % item[1])
        elif item[0] == STARTENDTAG:
            _startout(out, item, u"/>")
        else:
            wc.log.error(wc.LOG_FILTER, "unknown buffer element %s", item[0])
    return out


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
    'tag': _("Tag"),
    'tagname': _("Tag name"),
    'attr': _("Attribute"),
    'attrval': _("Attribute value"),
    'complete': _("Complete tag"),
    'enclosed': _("Enclosed block"),
}


# tags where close tag is missing
# note that this means that if the ending tag is there, it will not
# be filtered...
NO_CLOSE_TAGS = ('img', 'image', 'meta', 'br', 'link', 'area')


def part_num (s):
    """
    Translation: tag name ==> tag number.
    """
    for i, part in enumerate(partvalnames):
        if part == s:
            return i
    return None


def num_part (i):
    """
    Translation: tag number ==> tag name.
    """
    return partvalnames[i]


class RewriteRule (wc.filter.rules.UrlRule.UrlRule):
    """
    A rewrite rule applies to a specific tag, optional with attribute
    constraints (stored in self.attrs) or a regular expression to
    match the enclosed block (self.enclosed).
    """
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, tag=u"a", attrs=None, enclosed=u"",
                  part=COMPLETE, replacement=u""):
        """
        Initialize rule data.
        """
        super(RewriteRule, self).__init__(sid=sid, titles=titles,
                                  descriptions=descriptions, disable=disable)
        self.tag = tag
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        self.part = part
        self.replacement = replacement
        self.enclosed = enclosed
        if self.enclosed and self.tag in NO_CLOSE_TAGS:
            raise ValueError, "reading rule %r: tag %r has no end tag, " \
                              "so specifying an enclose value is invalid." % \
                              (self.titles['en'], tag)
        self.attrnames.append('tag')
        # we'll do this again in after parsing, in compile_data()
        self.set_start_sufficient()


    def fill_attrs (self, attrs, name):
        """
        Set attribute values.
        """
        super(RewriteRule, self).fill_attrs(attrs, name)
        if name == 'attr':
            val = attrs.get('name', u'href')
            self.current_attr = val
            self.attrs[self.current_attr] = u""
        elif name == 'replacement' and attrs.has_key('part'):
            self.part = part_num(attrs['part'])

    def end_data (self, name):
        super(RewriteRule, self).end_data(name)
        if name == 'attr':
            self.attrs[self.current_attr] = self._data
        elif name == 'enclosed':
            self.enclosed = self._data
        elif name == 'replacement':
            self.replacement = self._data

    def compile_data (self):
        """
        Compile url regular expressions.
        """
        super(RewriteRule, self).compile_data()
        wc.filter.rules.Rule.compileRegex(self, "enclosed")
        self.attrs_ro = {}
        for attr, val in self.attrs.items():
            self.attrs_ro[attr] = re.compile(val)
        self.set_start_sufficient()

    def update (self, rule, dryrun=False, log=None):
        """
        Update rewrite attributes with given rule data.
        """
        chg = super(RewriteRule, self).update(rule, dryrun=dryrun, log=log)
        attrs = ['attrs', 'part', 'replacement', 'enclosed']
        return self.update_attrs(attrs, rule, dryrun, log) or chg

    def _compute_start_sufficient (self):
        """
        Return True if start tag is sufficient for rule application.
        """
        if self.tag in NO_CLOSE_TAGS:
            return True
        return self.part not in [ENCLOSED, COMPLETE, TAG, TAGNAME]

    def set_start_sufficient (self):
        """
        Set flag to test if start tag is sufficient for rule application.
        """
        self.start_sufficient = self._compute_start_sufficient()

    def match_tag (self, tag):
        """
        Return True iff tag name matches this rule.
        """
        # XXX support regular expressions for self.tag
        return self.tag == tag

    def match_attrs (self, attrs):
        """
        Return True iff this rule matches given attributes.
        """
        occurred = []
        for attr, val in attrs.items():
            # attr or val could be None
            if attr is None:
                attr = ''
            if val is None:
                val = ''
            occurred.append(attr)
            ro = self.attrs_ro.get(attr)
            if ro and not ro.search(val):
                return False
        for attr in self.attrs.keys():
            if attr not in occurred:
                return False
        return True

    def match_complete (self, pos, tagbuf):
        """
        We know that the tag (and tag attributes) match. Now match
        the enclosing block. Return True on a match.
        """
        if not self.enclosed:
            # no enclosed expression => match
            return True
        # put buf items together for matching
        data = tagbuf2data(tagbuf[pos:], ZTUtils.FasterStringIO()).getvalue()
        return self.enclosed_ro.search(data)

    def filter_tag (self, tag, attrs, starttype):
        """
        Return filtered tag data for given tag and attributes.
        """
        wc.log.debug(wc.LOG_FILTER, "rule %s filter_tag", self.titles['en'])
        wc.log.debug(wc.LOG_FILTER, "original tag %r attrs %s", tag, attrs)
        wc.log.debug(wc.LOG_FILTER,
                "replace %s with %r", num_part(self.part), self.replacement)
        if self.part == COMPLETE:
            return [DATA, u""]
        if self.part == TAGNAME:
            return [starttype, self.replacement, attrs]
        if self.part == TAG:
            return [DATA, self.replacement]
        if self.part == ENCLOSED:
            return [starttype, tag, attrs]
        newattrs = {}
        # look for matching tag attributes
        for attr, val in attrs.items():
            ro = self.attrs_ro.get(attr)
            if ro:
                mo = ro.search(val)
                if mo:
                    if self.part == ATTR:
                        # replace complete attr, and make it possible
                        # for replacement to generate multiple attributes,
                        # eg "a=b c=d"
                        # XXX this is limited, but works so far
                        # XXX split does not honor quotes
                        for f in self.replacement.split():
                            if u'=' in self.replacement:
                                k, v = f.split(u'=')
                                newattrs[k] = mo.expand(v)
                            else:
                                newattrs[self.replacement] = None
                    elif self.part == ATTRVAL:
                        # backreferences are replaced
                        newattrs[attr] = mo.expand(self.replacement)
                    else:
                        wc.log.error(wc.LOG_FILTER,
                                     "Invalid part value %s", self.part)
                    continue
            # nothing matched, just append the attribute as is
            newattrs[attr] = val
        wc.log.debug(wc.LOG_FILTER,
                     "filtered tag %s attrs %s", tag, newattrs)
        return [starttype, tag, newattrs]

    def filter_complete (self, i, buf, tag):
        """
        Replace complete tag data in buf with replacement.
        """
        wc.log.debug(wc.LOG_FILTER, "rule %s filter_complete",
                     self.titles['en'])
        wc.log.debug(wc.LOG_FILTER, "original buffer %s", buf)
        wc.log.debug(wc.LOG_FILTER, "part %s", num_part(self.part))
        if self.part == COMPLETE:
            buf[i:] = [[DATA, self.replacement]]
        elif self.part == TAG:
            buf[i] = [DATA, self.replacement]
            buf.append([DATA, self.replacement])
        elif self.part == TAGNAME:
            buf[i] = [STARTTAG, self.replacement, {}]
            buf.append([ENDTAG, self.replacement])
        elif self.part == ENCLOSED:
            buf[i+1:] = [[DATA, self.replacement]]
            buf.append([ENDTAG, tag])
        wc.log.debug(wc.LOG_FILTER, "filtered buffer %s", buf)

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(RewriteRule, self).toxml()
        if self.tag != u'a':
            s += u'\n tag="%s"' % wc.XmlUtils.xmlquoteattr(self.tag)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        for key, val in self.attrs.items():
            s += u"\n  <attr"
            if key != u'href':
                s += u' name="%s"' % key
            if val:
                s += u">%s</attr>" % wc.XmlUtils.xmlquote(val)
            else:
                s += u"/>"
        if self.enclosed:
            s += u"\n  <enclosed>%s</enclosed>" % \
                 wc.XmlUtils.xmlquote(self.enclosed)
        if self.part != COMPLETE or self.replacement:
            s += u'\n  <replacement part="%s"' % num_part(self.part)
            if self.replacement:
                s += u">%s</replacement>" % \
                     wc.XmlUtils.xmlquote(self.replacement)
            else:
                s += u"/>"
        s += u"\n</%s>" % self.get_name()
        return s

    def __str__ (self):
        """
        Return rule data as string.
        """
        s = super(RewriteRule, self).__str__()
        s += "tag %s\n" % self.tag.encode("iso-8859-1")
        for key, val in self.attrs.items():
            s += "attr: %s, %r\n" % (key.encode("iso-8859-1"),
                                     val.encode("iso-8859-1"))
        s += "enclosed %r\n" % self.enclosed.encode("iso-8859-1")
        s += "part %s\n" % num_part(self.part)
        s += "replacement %r\n" % self.replacement.encode("iso-8859-1")
        s += "start suff. %d" % self.start_sufficient
        return s
