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

import urllib
import bk.HtmlParser
import bk.url
import wc.filter
import wc.filter.JSFilter
import wc.filter.rules.RewriteRule
import wc.filter.HtmlSecurity
import wc.filter.HtmlTags
import wc.filter.Rating


class HtmlFilter (wc.filter.JSFilter.JSFilter):
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
        self.security = wc.filter.HtmlSecurity.HtmlSecurity()


    def new_instance (self, **opts):
        return HtmlFilter(self.rules, self.ratings, self.url, **opts)


    def error (self, msg):
        """signal a filter/parser error"""
        bk.log.error(wc.LOG_FILTER, msg)


    def warning (self, msg):
        """signal a filter/parser warning"""
        bk.log.warn(wc.LOG_FILTER, msg)


    def fatalError (self, msg):
        """signal a fatal filter/parser error"""
        bk.log.critical(wc.LOG_FILTER, msg)


    def __repr__ (self):
        """representation with recursion level and state"""
        return "<HtmlFilter[%d] %s>" % (self.level, self.url)


    def _is_waiting (self, item):
        """if parser is in wait state put item on waitbuffer and return
           True"""
        if self.htmlparser.state[0]=='wait':
            self.htmlparser.waitbuf.append(item)
            return True
        return False


    def _data (self, d):
        """general handler for data"""
        item = [wc.filter.rules.RewriteRule.DATA, d]
        if self._is_waiting(item):
            return
        self.htmlparser.tagbuf.append(item)


    def cdata (self, data):
        """character data"""
        bk.log.debug(wc.LOG_FILTER, "%s cdata %r", self, data)
        return self._data(data)


    def characters (self, data):
        """characters"""
        bk.log.debug(wc.LOG_FILTER, "%s characters %r", self, data)
        return self._data(data)


    def comment (self, data):
        """a comment; accept only non-empty comments"""
        if not (self.comments and data):
            return
        bk.log.debug(wc.LOG_FILTER, "%s comment %r", self, data)
        item = [wc.filter.rules.RewriteRule.COMMENT, data]
        if self._is_waiting(item):
            return
        self.htmlparser.tagbuf.append(item)


    def doctype (self, data):
        bk.log.debug(wc.LOG_FILTER, "%s doctype %r", self, data)
        return self._data("<!DOCTYPE%s>"%data)


    def pi (self, data):
        bk.log.debug(wc.LOG_FILTER, "%s pi %r", self, data)
        return self._data("<?%s?>"%data)


    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        # default data
        bk.log.debug(wc.LOG_FILTER, "%s startElement %r", self, tag)
        if self._is_waiting([wc.filter.rules.RewriteRule.STARTTAG, tag, attrs]):
            return
        tag = wc.filter.HtmlTags.check_spelling(tag, self.url)
        if self.stackcount:
            if self.stackcount[-1][0]==tag:
                self.stackcount[-1][1] += 1
        if tag=="meta":
            if attrs.get('http-equiv', '').lower() == 'content-rating':
                rating = bk.HtmlParser.resolve_html_entities(attrs.get('content', ''))
                url, rating = wc.filter.Rating.rating_import(self.url, rating)
                # note: always put this in the cache, since this overrides
                # any http header setting, and page content changes more
                # often
                wc.filter.Rating.rating_add(url, rating)
        elif tag=="body":
            if self.ratings:
                # headers finished, check rating data
                for rule in self.ratings:
                    msg = wc.filter.Rating.rating_allow(self.url, rule)
                    if msg:
                        raise wc.filter.FilterRating(msg)
                self.ratings = []
        elif tag=="base" and attrs.has_key('href'):
            self.base_url = attrs['href']
            # some base urls are just the host name, eg. www.imadoofus.com
            if not urllib.splittype(self.base_url)[0]:
                self.base_url = "%s://%s" % \
                                (urllib.splittype(self.url)[0], self.base_url)
            self.base_url = bk.url.url_norm(self.base_url)
            bk.log.debug(wc.LOG_FILTER, "%s using base url %r", self, self.base_url)
        # search for and prevent known security flaws in HTML
        self.security.scan_start_tag(tag, attrs, self)
        # look for filter rules which apply
        self.filterStartElement(tag, attrs)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and not self.javascript:
            self.htmlparser.tagbuf2data()


    def filterStartElement (self, tag, attrs):
        """filter the start element according to filter rules"""
        rulelist = []
        filtered = False
        item = [wc.filter.rules.RewriteRule.STARTTAG, tag, attrs]
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                bk.log.debug(wc.LOG_FILTER, "%s matched rule %r on tag %r", self, rule.titles['en'], tag)
                if rule.start_sufficient:
                    item = rule.filter_tag(tag, attrs)
                    filtered = True
                    if item[0]==wc.filter.rules.RewriteRule.STARTTAG and item[1]==tag:
                        foo,tag,attrs = item
                        # give'em a chance to replace more than one attribute
                        continue
                    else:
                        break
                else:
                    bk.log.debug(wc.LOG_FILTER, "%s put rule %r on buffer", self, rule.titles['en'])
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
            self.jsStartElement(tag, attrs)
        else:
            # put original item on tag buffer
            self.htmlparser.tagbuf.append(item)


    def endElement (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the tag buffer (calling tagbuf2data)"""
        bk.log.debug(wc.LOG_FILTER, "%s endElement %r", self, tag)
        if self._is_waiting([wc.filter.rules.RewriteRule.ENDTAG, tag]):
            return
        tag = wc.filter.HtmlTags.check_spelling(tag, self.url)
        if self.stackcount and self.stackcount[-1][0]==tag:
            self.stackcount[-1][1] -= 1
        # search for and prevent known security flaws in HTML
        self.security.scan_end_tag(tag)
        item = [wc.filter.rules.RewriteRule.ENDTAG, tag]
        if not self.filterEndElement(tag):
            if self.javascript and tag=='script':
                self.jsEndElement(item)
                self.js_src = False
                return
            self.htmlparser.tagbuf.append(item)
        #XXX dont write any data to buf if there are still rating rules
        #if self.ratings and not finish:
        #    return
        if not self.rulestack:
            self.htmlparser.tagbuf2data()


    def filterEndElement (self, tag):
        """filters an end tag, return True if tag was filtered, else False"""
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag) and \
           self.stackcount[-1][0]==tag and self.stackcount[-1][1]<=0:
            del self.stackcount[-1]
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.htmlparser.tagbuf):
                    rule.filter_complete(pos, self.htmlparser.tagbuf, tag)
                    return True
        return False

