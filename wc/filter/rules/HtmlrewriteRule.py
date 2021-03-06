# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Rule rewriting html tags.
"""
import re
import urllib
from StringIO import StringIO
from wc import log, LOG_HTML, XmlUtils
from . import UrlRule, Rule
from ..html import (COMPLETE, ENCLOSED, MATCHED, ATTR, ATTRVAL,
    ATTRNAME, DATA, TAG, TAGNAME, ENDTAG, tagbuf2data)

# a list
partvalnames = [
    'tag',
    'tagname',
    'attr',
    'attrval',
    'attrname',
    'complete',
    'enclosed',
    'matched',
]
partnames = {
    'tag': _("Tag"),
    'tagname': _("Tag name"),
    'attr': _("Attribute"),
    'attrval': _("Attribute value"),
    'attrname': _("Attribute name"),
    'complete': _("Complete tag"),
    'enclosed': _("Enclosed block"),
    'matched': _("Matched content"),
}


# tags where close tag is missing
# note that this means that if the ending tag is there, it will not
# be filtered...
NO_CLOSE_TAGS = ('img', 'image', 'meta', 'br', 'link', 'area')


def part_num(s):
    """
    Translation: tag name ==> tag number.
    """
    for i, part in enumerate(partvalnames):
        if part == s:
            return i
    return None


def num_part(i):
    """
    Translation: tag number ==> tag name.
    """
    return partvalnames[i]


class HtmlrewriteRule(UrlRule.UrlRule):
    """
    A rewrite rule applies to a specific tag, optional with attribute
    constraints (stored in self.attrs) or a regular expression to
    match the enclosed content (self.contentmatch).
    """
    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, tag=u"a", attrs=None, contentmatch=u"",
                  part=COMPLETE, replacement=u""):
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
        self.contentmatch = contentmatch
        self.contentmatch_ro = None
        self.attrnames.append('tag')

    def fill_attrs(self, attrs, name):
        """
        Set attribute values.
        """
        super(HtmlrewriteRule, self).fill_attrs(attrs, name)
        if name == 'attr':
            val = attrs.get('name', u'href')
            self.current_attr = val
            self.attrs[self.current_attr] = u""
        elif name == 'replacement' and 'part' in attrs:
            self.part = part_num(attrs['part'])

    def end_data(self, name):
        """
        Store attr, contentmatch or replacement data.
        """
        super(HtmlrewriteRule, self).end_data(name)
        if name == 'attr':
            self.attrs[self.current_attr] = self._data
        elif name in ('enclosed', 'contentmatch'):
            # note: match in enclosed for backwards compatibility
            self.contentmatch = self._data
        elif name == 'replacement':
            self.replacement = self._data

    def compile_data(self):
        """
        Compile url regular expressions.
        """
        super(HtmlrewriteRule, self).compile_data()
        Rule.compileRegex(self, "contentmatch")
        Rule.compileRegex(self, "tag", fullmatch=True)
        # optimization: use string equality if tag is a plain string
        if self.tag.isalpha():
            self.match_tag = self._match_tag
        else:
            self.match_tag = self._match_tag_ro
        for attr, val in self.attrs.iteritems():
            self.attrs_ro[attr] = re.compile(val)
        if self.contentmatch:
            for tag in NO_CLOSE_TAGS:
                if self.match_tag(tag):
                    raise ValueError(
                              "reading rule %r: tag %r has no end tag, " \
                              "so specifying a contentmatch value is invalid." % \
                              (self.titles['en'], tag))

    def update(self, rule, dryrun=False, log=None):
        """
        Update rewrite attributes with given rule data.
        """
        chg = super(HtmlrewriteRule, self).update(rule, dryrun=dryrun,
                     log=log)
        attrs = ['attrs', 'part', 'replacement', 'contentmatch']
        return self.update_attrs(attrs, rule, dryrun, log) or chg

    def matches_starttag(self, tag):
        """See if this rule matches start tag."""
        if tag in NO_CLOSE_TAGS:
            return True
        return self.part not in [
            ENCLOSED,
            MATCHED,
            COMPLETE,
        ]

    def matches_endtag(self, tag):
        """See if this rule matches end tags."""
        if tag in NO_CLOSE_TAGS:
            return True
        return self.part not in [
            ATTR,
            ATTRVAL,
            ATTRNAME,
        ]

    def _match_tag_ro(self, tag):
        """
        Return True iff tag name matches this rule.
        """
        return self.tag_ro.search(tag)

    def _match_tag(self, tag):
        """
        Return True iff tag name matches this rule.
        """
        return self.tag == tag

    def match_attrs(self, attrs):
        """
        Return True iff this rule matches given attributes.
        """
        occurred = []
        for attr, val in attrs.iteritems():
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

    def match_complete(self, pos, tagbuf):
        """
        We know that the tag (and tag attributes) match. Now match
        the enclosing block, where pos points to the buffer start tag.
        Return True on a match.
        """
        if not self.contentmatch:
            # no contentmatch expression => match
            return True
        # put buf items together for matching, but without start tag
        items = tagbuf[pos+1:]
        data = tagbuf2data(items, StringIO()).getvalue()
        return self.contentmatch_ro.search(data)

    def filter_tag(self, tag, attrs, starttype):
        """Return filtered tag data for given tag and attributes."""
        log.debug(LOG_HTML, "rule %s filter_tag", self.titles['en'])
        log.debug(LOG_HTML, "original tag %r attrs %s", tag, attrs)
        log.debug(LOG_HTML,
                 "replace %s with %r", num_part(self.part), self.replacement)
        if self.part == COMPLETE:
            return [DATA, u""]
        if self.part == TAGNAME:
            return [starttype, self.replacement, attrs]
        if self.part == TAG:
            return [DATA, self.replacement]
        if self.part in (ENCLOSED, MATCHED):
            return [starttype, tag, attrs]
        newattrs = {}
        # look for matching tag attributes
        for attr, val in attrs.iteritems():
            ro = self.attrs_ro.get(attr)
            if ro:
                mo = ro.search(val)
                if mo:
                    if self.part == ATTR:
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
                    elif self.part == ATTRVAL:
                        # backreferences are replaced
                        val = mo.expand(self.replacement)
                        if "url" in mo.groupdict():
                            val = urllib.unquote(val)
                        newattrs[attr] = val
                    elif self.part == ATTRNAME:
                        newattr = mo.expand(self.replacement)
                        newattrs[newattr] = val
                    else:
                        log.error(LOG_HTML,
                                     "Invalid part value %s", self.part)
                    continue
            # nothing matched, just append the attribute as is
            newattrs[attr] = val
        log.debug(LOG_HTML, "filtered tag %s attrs %s", tag, newattrs)
        return [starttype, tag, newattrs]

    def filter_complete(self, i, buf, tag, mo):
        """Replace tag data in buf with replacement."""
        log.debug(LOG_HTML, "rule %s filter_complete", self.titles['en'])
        log.debug(LOG_HTML, "original buffer %s", buf)
        log.debug(LOG_HTML, "part %s", num_part(self.part))
        if self.part == COMPLETE:
            buf[i:] = [[DATA, self.replacement]]
        elif self.part == TAG:
            buf.append([DATA, self.replacement])
        elif self.part == TAGNAME:
            buf.append([ENDTAG, self.replacement])
        elif self.part == ENCLOSED:
            buf[i+1:] = [[DATA, self.replacement]]
            buf.append([ENDTAG, tag])
        elif self.part == MATCHED:
            replacement = mo.string[:mo.start()] + mo.string[mo.end():]
            buf[i+1:] = [[DATA, replacement]]
            buf.append([ENDTAG, tag])
        log.debug(LOG_HTML, "filtered buffer %s", buf)

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(HtmlrewriteRule, self).toxml()
        s += u'\n tag="%s"' % XmlUtils.xmlquoteattr(self.tag)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        for key, val in self.attrs.iteritems():
            s += u'\n  <attr name="%s"' % XmlUtils.xmlquoteattr(key)
            if val:
                s += u">%s</attr>" % XmlUtils.xmlquote(val)
            else:
                s += u"/>"
        if self.contentmatch:
            s += u"\n  <contentmatch>%s</contentmatch>" % \
                 XmlUtils.xmlquote(self.contentmatch)
        s += u'\n  <replacement part="%s"' % num_part(self.part)
        if self.replacement:
            s += u">%s</replacement>" % XmlUtils.xmlquote(self.replacement)
        else:
            s += u"/>"
        s += u"\n</%s>" % self.name
        return s

    def __str__(self):
        """
        Return rule data as string.
        """
        s = super(HtmlrewriteRule, self).__str__()
        s += "tag %s\n" % self.tag.encode("iso-8859-1")
        for key, val in self.attrs.iteritems():
            s += "attr: %s, %r\n" % (key.encode("iso-8859-1"),
                                     val.encode("iso-8859-1"))
        s += "contentmatch %r\n" % self.contentmatch.encode("iso-8859-1")
        s += "part %s\n" % num_part(self.part)
        s += "replacement %r\n" % self.replacement.encode("iso-8859-1")
        return s
