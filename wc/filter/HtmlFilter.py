# -*- coding: iso-8859-1 -*-
"""filter a HTML stream."""
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

import re, urllib, wc
from wc.parser import resolve_html_entities
from wc.filter import FilterRating
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc.filter.Rating import rating_import, rating_add, rating_allow
from wc.filter.JSFilter import JSFilter
from wc.log import *
from HtmlTags import check_spelling
from HtmlSecurity import HtmlSecurity


class HtmlFilter (JSFilter):
    """Filtering HTML parser handler. Has filter rules and a rule stack.
       The callbacks modify parser state and buffers.

       XXX fixme: should make internal functions start with _
    """

    def __init__ (self, rules, ratings, url, **opts):
        "init rules and buffers"
        super(HtmlFilter, self).__init__(url, opts)
        self.rules = rules
        self.ratings = ratings
        self.rulestack = []
        self.stackcount = []
        self.base_url = None
        # for security flaw scanning
        self.security = HtmlSecurity()


    def error (self, msg):
        """signal a filter/parser error"""
        error(FILTER, msg)


    def warning (self, msg):
        """signal a filter/parser warning"""
        warn(FILTER, msg)


    def fatalError (self, msg):
        """signal a fatal filter/parser error"""
        critical(FILTER, msg)


    def __repr__ (self):
        """representation with recursion level and state"""
        return "<HtmlFilter[%d] %s>" % (self.level, self.url)


    def _data (self, d):
        """general handler for data"""
        item = [DATA, d]
        self.htmlparser.tagbuf.append(item)


    def cdata (self, data):
        """character data"""
        self._debug("cdata %r", data)
        return self._data(data)


    def characters (self, data):
        """characters"""
        self._debug("characters %r", data)
        return self._data(data)


    def comment (self, data):
        """a comment; accept only non-empty comments"""
        if not (self.comments and data):
            return
        self._debug("comment %r", data)
        item = [COMMENT, data]
        self.htmlparser.tagbuf.append(item)


    def doctype (self, data):
        self._debug("doctype %r", data)
        return self._data("<!DOCTYPE%s>"%data)


    def pi (self, data):
        self._debug("pi %r", data)
        return self._data("<?%s?>"%data)


    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        # default data
        self._debug("startElement %r", tag)
        tag = check_spelling(tag, self.url)
        if self.stackcount:
            if self.stackcount[-1][0]==tag:
                self.stackcount[-1][1] += 1
        if tag=="meta":
            if attrs.get('http-equiv', '').lower() =='content-rating':
                rating = resolve_html_entities(attrs.get('content', ''))
                url, rating = rating_import(url, rating)
                # note: always put this in the cache, since this overrides
                # any http header setting, and page content changes more
                # often
                rating_add(url, rating)
        elif tag=="body":
            if self.ratings:
                # headers finished, check rating data
                for rule in self.ratings:
                    msg = rating_allow(self.url, rule)
                    if msg:
                        raise FilterRating(msg)
                self.ratings = []
        elif tag=="base" and attrs.has_key('href'):
            self.base_url = attrs['href']
            # some base urls are just the host name, eg. www.imadoofus.com
            if not urllib.splittype(self.base_url)[0]:
                self.base_url = "%s://%s" % \
                                (urllib.splittype(self.url)[0], self.base_url)
            self._debug("using base url %r", self.base_url)
        # search for and prevent known security flaws in HTML
        self.security.scan_start_tag(tag, attrs, self)
        # look for filter rules which apply
        self._filterStartElement(tag, attrs)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and not self.javascript:
            self.htmlparser.tagbuf2data()


    def _filterStartElement (self, tag, attrs):
        """filter the start element according to filter rules"""
        rulelist = []
        filtered = False
        item = [STARTTAG, tag, attrs]
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                self._debug("matched rule %r on tag %r", rule.title, tag)
                if rule.start_sufficient:
                    item = rule.filter_tag(tag, attrs)
                    filtered = True
                    if item[0]==STARTTAG and item[1]==tag:
                        foo,tag,attrs = item
                        # give'em a chance to replace more than one attribute
                        continue
                    else:
                        break
                else:
                    self._debug("put on buffer")
                    rulelist.append(rule)
        if rulelist:
            # remember buffer position for end tag matching
            pos = len(self.htmlparser.tagbuf)
            self.rulestack.append((pos, rulelist))
            self.stackcount.append([tag, 1])
        if filtered:
            # put filtered item on tag buffer
            self.htmlparser.tagbuf.append(item)
        elif self.javascript:
            # if it's not yet filtered, try filter javascript
            self._jsStartElement(tag, attrs)
        else:
            # put original item on tag buffer
            self.htmlparser.tagbuf.append(item)


    def endElement (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the tag buffer (calling tagbuf2data)"""
        self._debug("endElement %r", tag)
        tag = check_spelling(tag, self.url)
        if self.stackcount and self.stackcount[-1][0]==tag:
            self.stackcount[-1][1] -= 1

        # search for and prevent known security flaws in HTML
        self.security.scan_end_tag(tag)
        item = [ENDTAG, tag]
        if not self._filterEndElement(tag):
            if self.javascript and tag=='script':
                self._jsEndElement(item)
                self.js_src = False
                return
            self.htmlparser.tagbuf.append(item)
        #XXX dont write any data to buf if there are still rating rules
        #if self.ratings and not finish:
        #    return
        if not self.rulestack:
            self.htmlparser.tagbuf2data()


    def _filterEndElement (self, tag):
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag) and \
           self.stackcount[-1][0]==tag and self.stackcount[-1][1]<=0:
            del self.stackcount[-1]
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.htmlparser.tagbuf):
                    rule.filter_complete(pos, self.htmlparser.tagbuf)
                    return True
        return False

