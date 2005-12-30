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
from StringIO import StringIO

import wc
import wc.log
import wc.XmlUtils
import wc.filter.rules.UrlRule
import wc.filter.rules.Rule
import wc.filter.html
import wc.HtmlParser.htmllib

# a list
partvalnames = [
    'tag',
    'tagname',
    'attr',
    'attrval',
    'attrname',
    'complete',
    'enclosed',
]
partnames = {
    'tag': _("Tag"),
    'tagname': _("Tag name"),
    'attr': _("Attribute"),
    'attrval': _("Attribute value"),
    'attrname': _("Attribute name"),
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


class HtmlrewriteRule (wc.filter.rules.UrlRule.UrlRule):
    """
    A rewrite rule applies to a specific tag, optional with attribute
    constraints (stored in self.attrs) or a regular expression to
    match the enclosed block (self.enclosed).
    """
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, tag=u"a", attrs=None, enclosed=u"",
                  part=wc.filter.html.COMPLETE, replacement=u""):
        """
        Initialize rule data.
        """
        super(HtmlrewriteRule, self).__init__(sid=sid, titles=titles,
                                  descriptions=descriptions, disable=disable)
        self.tag = tag
        self.tag_ro = None
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        self.attrs_ro = {}
        self.part = part
        self.replacement = replacement
        self.enclosed = enclosed
        self.enclosed_ro = None
        self.attrnames.append('tag')

    def fill_attrs (self, attrs, name):
        """
        Set attribute values.
        """
        super(HtmlrewriteRule, self).fill_attrs(attrs, name)
        if name == 'attr':
            val = attrs.get('name', u'href')
            self.current_attr = val
            self.attrs[self.current_attr] = u""
        elif name == 'replacement' and attrs.has_key('part'):
            self.part = part_num(attrs['part'])

    def end_data (self, name):
        """
        Store attr, enclosed or replacement data.
        """
        super(HtmlrewriteRule, self).end_data(name)
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
        super(HtmlrewriteRule, self).compile_data()
        wc.filter.rules.Rule.compileRegex(self, "enclosed")
        wc.filter.rules.Rule.compileRegex(self, "tag", fullmatch=True)
        # optimization: use string equality if tag is a plain string
        if self.tag.isalpha():
            self.match_tag = self._match_tag
        else:
            self.match_tag = self._match_tag_ro
        for attr, val in self.attrs.items():
            self.attrs_ro[attr] = re.compile(val)
        if self.enclosed:
            for tag in NO_CLOSE_TAGS:
                if self.match_tag(tag):
                    raise ValueError(
                              "reading rule %r: tag %r has no end tag, " \
                              "so specifying an enclose value is invalid." % \
                              (self.titles['en'], tag))

    def update (self, rule, dryrun=False, log=None):
        """
        Update rewrite attributes with given rule data.
        """
        chg = super(HtmlrewriteRule, self).update(rule, dryrun=dryrun,
                     log=log)
        attrs = ['attrs', 'part', 'replacement', 'enclosed']
        return self.update_attrs(attrs, rule, dryrun, log) or chg

    def matches_starttag (self):
        """
        See if this rule matches start tags.
        """
        for tag in NO_CLOSE_TAGS:
            if self.match_tag(tag):
                return True
        return self.part not in [
            wc.filter.html.ENCLOSED,
            wc.filter.html.COMPLETE,
        ]

    def matches_endtag (self):
        """
        See if this rule matches end tags.
        """
        for tag in NO_CLOSE_TAGS:
            if self.match_tag(tag):
                return False
        return self.part not in [
            wc.filter.html.ATTR,
            wc.filter.html.ATTRVAL,
            wc.filter.html.ATTRNAME,
        ]

    def _match_tag_ro (self, tag):
        """
        Return True iff tag name matches this rule.
        """
        return self.tag_ro.search(tag)

    def _match_tag (self, tag):
        """
        Return True iff tag name matches this rule.
        """
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
        # Check if every attribute matched.
        for attr in self.attrs:
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
        items = tagbuf[pos:]
        data = wc.filter.html.tagbuf2data(items, StringIO()).getvalue()
        return self.enclosed_ro.match(data)

    def filter_tag (self, tag, attrs, starttype):
        """
        Return filtered tag data for given tag and attributes.
        """
        assert wc.log.debug(wc.LOG_HTML,
                            "rule %s filter_tag", self.titles['en'])
        assert wc.log.debug(wc.LOG_HTML,
                            "original tag %r attrs %s", tag, attrs)
        assert wc.log.debug(wc.LOG_HTML,
                 "replace %s with %r", num_part(self.part), self.replacement)
        if self.part == wc.filter.html.COMPLETE:
            return [wc.filter.html.DATA, u""]
        if self.part == wc.filter.html.TAGNAME:
            return [starttype, self.replacement, attrs]
        if self.part == wc.filter.html.TAG:
            return [wc.filter.html.DATA, self.replacement]
        if self.part == wc.filter.html.ENCLOSED:
            return [starttype, tag, attrs]
        newattrs = {}
        # look for matching tag attributes
        for attr, val in attrs.items():
            ro = self.attrs_ro.get(attr)
            if ro:
                mo = ro.search(val)
                if mo:
                    if self.part == wc.filter.html.ATTR:
                        # replace complete attr, and make it possible
                        # for replacement to generate multiple attributes,
                        # eg "a=b c=d"
                        # XXX this is limited, but works so far
                        for f in self.replacement.split():
                            if u'=' in self.replacement:
                                k, v = f.split(u'=', 1)
                                newattrs[k] = mo.expand(v)
                            else:
                                newattrs[self.replacement] = None
                    elif self.part == wc.filter.html.ATTRVAL:
                        # backreferences are replaced
                        newattrs[attr] = mo.expand(self.replacement)
                    elif self.part == wc.filter.html.ATTRNAME:
                        newattr = mo.expand(self.replacement)
                        newattrs[newattr] = val
                    else:
                        wc.log.error(wc.LOG_HTML,
                                     "Invalid part value %s", self.part)
                    continue
            # nothing matched, just append the attribute as is
            newattrs[attr] = val
        assert wc.log.debug(wc.LOG_HTML,
                     "filtered tag %s attrs %s", tag, newattrs)
        return [starttype, tag, newattrs]

    def filter_complete (self, i, buf, tag):
        """
        Replace complete tag data in buf with replacement.
        """
        assert wc.log.debug(wc.LOG_HTML, "rule %s filter_complete",
                     self.titles['en'])
        assert wc.log.debug(wc.LOG_HTML, "original buffer %s", buf)
        assert wc.log.debug(wc.LOG_HTML, "part %s", num_part(self.part))
        if self.part == wc.filter.html.COMPLETE:
            buf[i:] = [[wc.filter.html.DATA, self.replacement]]
        elif self.part == wc.filter.html.TAG:
            buf.append([wc.filter.html.DATA, self.replacement])
        elif self.part == wc.filter.html.TAGNAME:
            buf.append([wc.filter.html.ENDTAG, self.replacement])
        elif self.part == wc.filter.html.ENCLOSED:
            buf[i+1:] = [[wc.filter.html.DATA, self.replacement]]
            buf.append([wc.filter.html.ENDTAG, tag])
        assert wc.log.debug(wc.LOG_HTML, "filtered buffer %s", buf)

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(HtmlrewriteRule, self).toxml()
        s += u'\n tag="%s"' % wc.XmlUtils.xmlquoteattr(self.tag)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        for key, val in self.attrs.items():
            s += u'\n  <attr name="%s"' % wc.XmlUtils.xmlquoteattr(key)
            if val:
                s += u">%s</attr>" % wc.XmlUtils.xmlquote(val)
            else:
                s += u"/>"
        if self.enclosed:
            s += u"\n  <enclosed>%s</enclosed>" % \
                 wc.XmlUtils.xmlquote(self.enclosed)
        if self.part != wc.filter.html.COMPLETE or self.replacement:
            s += u'\n  <replacement part="%s"' % num_part(self.part)
            if self.replacement:
                s += u">%s</replacement>" % \
                     wc.XmlUtils.xmlquote(self.replacement)
            else:
                s += u"/>"
        s += u"\n</%s>" % self.name
        return s

    def __str__ (self):
        """
        Return rule data as string.
        """
        s = super(HtmlrewriteRule, self).__str__()
        s += "tag %s\n" % self.tag.encode("iso-8859-1")
        for key, val in self.attrs.items():
            s += "attr: %s, %r\n" % (key.encode("iso-8859-1"),
                                     val.encode("iso-8859-1"))
        s += "enclosed %r\n" % self.enclosed.encode("iso-8859-1")
        s += "part %s\n" % num_part(self.part)
        s += "replacement %r\n" % self.replacement.encode("iso-8859-1")
        return s
