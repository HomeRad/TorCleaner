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
Filter a HTML stream.
"""

import urllib

import wc.HtmlParser
import wc.url
import wc.log
import wc.filter
import wc.filter.html
import wc.filter.html.JSFilter
import wc.filter.html.HtmlSecurity
import wc.filter.rating


class HtmlFilter (wc.filter.html.JSFilter.JSFilter):
    """
    Filtering HTML parser handler. Has filter rules and a rule stack.
    The callbacks modify parser state and buffers.

    XXX fixme: should make internal functions start with _
    """

    def __init__ (self, rules, ratings, url, localhost, **opts):
        """
        Init rules and buffers.
        """
        super(HtmlFilter, self).__init__(url, localhost, opts)
        self.rules = rules
        self.ratings = ratings
        self.rulestack = []
        self.stackcount = []
        self.base_url = None
        # for security flaw scanning
        self.security = wc.filter.html.HtmlSecurity.HtmlSecurity()

    def new_instance (self, **opts):
        """
        Make a new instance of this filter, for recursive filtering.
        """
        return HtmlFilter(self.rules, self.ratings, self.url,
                          self.localhost, **opts)

    def error (self, msg):
        """
        Report a filter/parser error.
        """
        wc.log.error(wc.LOG_FILTER, msg)

    def warning (self, msg):
        """
        Report a filter/parser warning.
        """
        wc.log.warn(wc.LOG_FILTER, msg)

    def fatal_error (self, msg):
        """
        Report a fatal filter/parser error.
        """
        wc.log.critical(wc.LOG_FILTER, msg)

    def __repr__ (self):
        """
        Representation with recursion level and state.
        """
        return "<HtmlFilter[%d] %s>" % (self.level, self.url)

    def _is_waiting (self, item):
        """
        If parser is in wait state put item on waitbuffer and return True.
        """
        if self.htmlparser.state[0] == 'wait':
            self.htmlparser.waitbuf.append(item)
            return True
        return False

    def _data (self, data):
        """
        General handler for data.
        """
        item = [wc.filter.html.DATA, data]
        if self._is_waiting(item):
            return
        self.htmlparser.tagbuf.append(item)

    def cdata (self, data):
        """
        Character data.
        """
        wc.log.debug(wc.LOG_FILTER, "%s cdata %r", self, data)
        return self._data(data)

    def characters (self, data):
        """
        Characters.
        """
        wc.log.debug(wc.LOG_FILTER, "%s characters %r", self, data)
        return self._data(data)

    def comment (self, data):
        """
        A comment; accept only non-empty comments.
        """
        if not (self.comments and data):
            return
        wc.log.debug(wc.LOG_FILTER, "%s comment %r", self, data)
        item = [wc.filter.html.COMMENT, data]
        if self._is_waiting(item):
            return
        self.htmlparser.tagbuf.append(item)

    def doctype (self, data):
        """
        HTML doctype.
        """
        wc.log.debug(wc.LOG_FILTER, "%s doctype %r", self, data)
        return self._data(u"<!DOCTYPE%s>" % data)

    def pi (self, data):
        """
        HTML pi.
        """
        wc.log.debug(wc.LOG_FILTER, "%s pi %r", self, data)
        return self._data(u"<?%s?>" % data)

    def start_element (self, tag, attrs):
        """
        HTML start element.
        """
        self._start_element(tag, attrs, False)

    def start_end_element (self, tag, attrs):
        """
        HTML start-end element (<a/>).
        """
        self._start_element(tag, attrs, True)

    def _start_element (self, tag, attrs, startend):
        """
        We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list.
        """
        # default data
        wc.log.debug(wc.LOG_FILTER, "%s start_element %r %s", self, tag, attrs)
        if self._is_waiting([wc.filter.html.STARTTAG,
                             tag, attrs]):
            return
        tag = wc.filter.html.check_spelling(tag, self.url)
        if self.stackcount and not startend:
            if self.stackcount[-1][0] == tag:
                self.stackcount[-1][1] += 1
        if tag == "meta":
            if attrs.get('http-equiv', u'').lower() == 'content-rating':
                rating = wc.HtmlParser.resolve_html_entities(
                                                  attrs.get('content', u''))
                url, rating = wc.filter.rating.rating_import(self.url, rating)
                # note: always put this in the cache, since this overrides
                # any http header setting, and page content changes more
                # often
                wc.filter.rating.rating_add(url, rating)
        elif tag == "body":
            if self.ratings:
                # headers finished, check rating data
                for rule in self.ratings:
                    msg = rule.rating_allow(self.url)
                    if msg:
                        raise wc.filter.FilterRating, msg
                self.ratings = []
        elif tag == "base" and attrs.has_key('href'):
            self.base_url = attrs['href']
            # some base urls are just the host name, eg. www.imadoofus.com
            if not urllib.splittype(self.base_url)[0]:
                self.base_url = "%s://%s" % \
                                (urllib.splittype(self.url)[0], self.base_url)
            self.base_url = wc.url.url_norm(self.base_url)[0]
            wc.log.debug(wc.LOG_FILTER, "%s using base url %r",
                         self, self.base_url)
        # search for and prevent known security flaws in HTML
        self.security.scan_start_tag(tag, attrs, self)
        # look for filter rules which apply
        self.filter_start_element(tag, attrs, startend)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and not self.javascript:
            self.htmlparser.tagbuf2data()

    def filter_start_element (self, tag, attrs, startend):
        """
        Filter the start element according to filter rules.
        """
        rulelist = []
        filtered = False
        if startend:
            starttype = wc.filter.html.STARTENDTAG
        else:
            starttype = wc.filter.html.STARTTAG
        item = [starttype, tag, attrs]
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                wc.log.debug(wc.LOG_FILTER, "%s matched rule %r on tag %r",
                             self, rule.titles['en'], tag)
                if rule.start_sufficient:
                    item = rule.filter_tag(tag, attrs, starttype)
                    filtered = True
                    if item[0] == starttype and item[1] == tag:
                        foo, tag, attrs = item
                        # give'em a chance to replace more than one attribute
                        continue
                    else:
                        break
                else:
                    wc.log.debug(wc.LOG_FILTER, "%s put rule %r on buffer",
                                 self, rule.titles['en'])
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
            self.js_start_element(tag, attrs)
        else:
            # put original item on tag buffer
            self.htmlparser.tagbuf.append(item)

    def end_element (self, tag):
        """
        We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
        If it matches and the rule stack is now empty we can flush
        the tag buffer (calling tagbuf2data).
        """
        wc.log.debug(wc.LOG_FILTER, "%s end_element %r", self, tag)
        if self._is_waiting([wc.filter.html.ENDTAG, tag]):
            return
        tag = wc.filter.html.check_spelling(tag, self.url)
        if self.stackcount and self.stackcount[-1][0] == tag:
            self.stackcount[-1][1] -= 1
        # search for and prevent known security flaws in HTML
        self.security.scan_end_tag(tag)
        item = [wc.filter.html.ENDTAG, tag]
        if not self.filter_end_element(tag):
            if self.javascript and tag == 'script':
                self.js_end_element(item)
                self.js_src = False
                return
            self.htmlparser.tagbuf.append(item)
        #XXX don't write any data to buf if there are still rating rules
        #if self.ratings and not finish:
        #    return
        if not self.rulestack:
            self.htmlparser.tagbuf2data()

    def filter_end_element (self, tag):
        """
        Filters an end tag, return True if tag was filtered, else False.
        """
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag) and \
           self.stackcount[-1][0] == tag and self.stackcount[-1][1] <= 0:
            del self.stackcount[-1]
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.htmlparser.tagbuf):
                    rule.filter_complete(pos, self.htmlparser.tagbuf, tag)
                    return True
        return False
