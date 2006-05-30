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
Rule rewriting xml tags.
"""

import re
import locale
import UrlRule
import wc.filter.html.RssHtmlFilter
import wc.filter.html.HtmlFilter

# valid replace types
RSSHTML = 0
REMOVE = 1

replacetypenames = {
    RSSHTML: u"rsshtml",
    REMOVE: u"remove",
}

replacetypenums = {
    u"rsshtml": RSSHTML,
    u"remove": REMOVE,
}


# xpath patterns and regex
_attr_pat = r"[a-z:]+=.+"
_xpath_attr_pat = r"(?P<tag>[a-z:]+)\[(?P<attrs>(%s(,%s)*))\]" % \
                  (_attr_pat, _attr_pat)
_xpath_attr_ro = re.compile(_xpath_attr_pat)

def parse_xpath (xpath):
    """
    Parse a simplified XPath expression into a selector list.
    """
    if not xpath:
        return []
    l = xpath.split('/')
    res = []
    for entry in l:
        mo = _xpath_attr_ro.match(entry)
        if mo:
            entry = mo.group("tag")
            attrs = [x.split("=", 1) for x in mo.group("attrs").split(",")]
        else:
            attrs = []
        res.append((entry, attrs))
    return res


def serialize_xpath (xpath):
    res = []
    for entry, attrs in xpath:
        if attrs:
            x = [u"%s=%s" % (attr, value) for attr, value in attrs]
            res.append(u"%s[%s]" % (entry, ",".join(x)))
        else:
            res.append(entry)
    return u"/".join(res)


def match_stack (stack, selector):
    if not stack or not selector:
        # both stack and selector must have items
        return False
    # i points initially at end of selector and decrements to the
    # beginning
    i = len(selector) - 1
    # compare from the end of the stack list
    for element in reversed(stack):
        if element[0] != wc.filter.xmlfilt.STARTTAG:
            continue
        tag = element[1]
        attrs = element[2]
        if i >= 0 and match_element(tag, attrs, selector[i]):
            if i == 0:
                break
            i -= 1
            continue
        return False
    # if i points to the beginning of selector, the document matches
    return i == 0


def match_element (tag, attrs, element_match):
    if tag != element_match[0]:
        return False
    for key, val in element_match[1]:
        if key not in attrs:
            return False
        if attrs[key] != val:
            return False
    return True


class XmlrewriteRule (UrlRule.UrlRule):
    """
    An XML rule first matches a document selector (which is a simple
    XPath expression) to select the correct XML documents this rule
    cares for.
    After that is ensured, each XML tag is matched against the list of
    replacements. Replacement matching occurs in order and allows for
    more than one replacment rule to trigger.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, selector=u"", replacetype=u"rsshtml",
                  value=u""):
        """
        Initialize rule data.
        """
        super(XmlrewriteRule, self).__init__(sid=sid, titles=titles,
                                 descriptions=descriptions, disable=disable)
        self.selector = selector
        self.selector_list = parse_xpath(selector)
        self.replacetype = replacetype
        self.value = value
        self.attrnames.extend(("selector", "replacetype", "value"))

    def compile_data (self):
        """
        Parse selector and set replacetype value.
        """
        super(XmlrewriteRule, self).compile_data()
        self.selector_list = parse_xpath(self.selector)
        self.replacetypenum = replacetypenums.get(self.replacetype, RSSHTML)
        if self.replacetypenum == RSSHTML:
            self.rsshtml = wc.filter.html.RssHtmlFilter.RssHtmlFilter()

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = super(XmlrewriteRule, self).toxml()
        quote = wc.XmlUtils.xmlquoteattr
        s += u'\n selector="%s"' % quote(self.selector)
        s += u'\n replacetype="%s"' % quote(self.replacetype)
        if self.value:
            s += u'\n value="%s"' % quote(self.value)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.name
        return s

    def __str__ (self):
        """
        Return rule data as string.
        """
        enc = locale.getpreferredencoding()
        s = super(XmlrewriteRule, self).__str__()
        s += "selector %s\n" % self.selector.encode(enc)
        replace = self.replacetype.encode(enc)
        value = self.value.encode(enc)
        s += "replace %s %r\n" % (replace, value)
        return s

    def match_tag (self, stack):
        """
        Match XML tag to given stack of XML elements.
        """
        return match_stack(stack, self.selector_list)

    def filter_tag (self, pos, tagbuf, tag, url, htmlrules):
        """
        Filter XML tag data.
        """
        if self.replacetypenum == RSSHTML:
            for item in tagbuf[pos:]:
                if item[0] == wc.filter.xmlfilt.DATA:
                    data = item[1]
                    data = self.filter_html(data, url, htmlrules)
                    data = self.rsshtml.filter(data, url, htmlrules)
                    item[1] = data
                    if "]]>" not in data:
                        item[0] = wc.filter.xmlfilt.CDATA
            tagbuf.append([wc.filter.xmlfilt.ENDTAG, tag])
        elif self.replacetypenum == REMOVE:
            del tagbuf[pos:]
        else:
            wc.log.warn(wc.LOG_XML, "%s: unimplemented replace type", self)

    def filter_html (self, data, url, htmlrules):
        """
        Filter HTML data.
        """
        # generate the HTML filter
        ratings = []
        localhost = "localhost"
        filt = wc.filter.html.HtmlFilter.HtmlFilter
        handler = filt(htmlrules, ratings, url, localhost,
                       comments=False, jscomments=False, javascript=False)
        p = wc.filter.html.HtmlParser.HtmlParser(handler)
        #htmlparser.debug(1)
        # the handler is modifying parser buffers and state
        handler.htmlparser = p
        # XXX remove encoding when HTML parser supports unicode
        encoding = "iso8859-1"
        data = data.encode(encoding, "ignore")
        p.feed(data)
        p.flush()
        p.tagbuf2data()
        return p.getoutput().decode(encoding)
