# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2008 Bastian Kleineidam
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
import wc.filter.html
import JSFilter
import HtmlSecurity
import wc.rating
import wc.configuration


class HtmlFilter (JSFilter.JSFilter):
    """Filtering HTML parser handler. Has filter rules and a rule stack.
    The callbacks modify parser state and buffers."""

    def __init__ (self, rules, ratings, url, localhost, **opts):
        """Init rules and buffers."""
        super(HtmlFilter, self).__init__(url, localhost, opts)
        self.rules = rules
        self.ratings = ratings
        self.rating = wc.rating.Rating()
        self.rulestack = []
        self.stackcount = []
        self.base_url = None
        # for security flaw scanning
        self.security = HtmlSecurity.HtmlSecurity()
        # cache rule match_tag into {tag -> list of rules}
        self.rule_tag_cache = {}
        assert None == wc.log.debug(wc.LOG_HTML,
                            "%s with %d rules", self, len(self.rules))

    def new_instance (self, **opts):
        """Make a new instance of this filter, for recursive filtering."""
        return HtmlFilter(self.rules, self.ratings, self.url,
                          self.localhost, **opts)

    def __repr__ (self):
        """Representation with recursion level and state."""
        return "<HtmlFilter[%d] %s)>" % (self.level, self.url)

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
        assert None == wc.log.debug(wc.LOG_HTML, "%s cdata %r", self, data)
        return self._data(data)

    def characters (self, data):
        """
        Characters.
        """
        assert None == wc.log.debug(wc.LOG_HTML,
            "%s characters %r", self, data)
        return self._data(data)

    def comment (self, data):
        """
        A comment; accept only non-empty comments.
        """
        if not (self.comments and data):
            return
        assert None == wc.log.debug(wc.LOG_HTML, "%s comment %r", self, data)
        item = [wc.filter.html.COMMENT, data]
        if self._is_waiting(item):
            return
        self.htmlparser.tagbuf.append(item)

    def doctype (self, data):
        """
        HTML doctype.
        """
        assert None == wc.log.debug(wc.LOG_HTML, "%s doctype %r", self, data)
        return self._data(u"<!DOCTYPE%s>" % data)

    def pi (self, data):
        """
        HTML pi.
        """
        assert None == wc.log.debug(wc.LOG_HTML, "%s pi %r", self, data)
        return self._data(u"<?%s?>" % data)

    def start_element (self, tag, attrs):
        """
        HTML start element.
        """
        assert None == wc.log.debug(wc.LOG_HTML,
                     "%s start_element %r %s", self, tag, attrs)
        self._start_element(tag, attrs, wc.filter.html.STARTTAG)

    def start_end_element (self, tag, attrs):
        """
        HTML start-end element (<a/>).
        """
        assert None == wc.log.debug(wc.LOG_HTML,
                     "%s start_end_element %r %s", self, tag, attrs)
        self._start_element(tag, attrs, wc.filter.html.STARTENDTAG)

    def _start_element (self, tag, attrs, starttype):
        """
        We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list.
        """
        if self._is_waiting([starttype, tag, attrs]):
            return
        tag = wc.filter.html.check_spelling(tag, self.url)
        if self.stackcount and \
           starttype == wc.filter.html.STARTTAG and \
           self.stackcount[-1][0] == tag:
            self.stackcount[-1][1] += 1
        if tag == "img":
            if attrs.has_key("alt") and not attrs.has_key("title"):
                # Mozilla only displays title as tooltip.
                title = attrs.get_true('alt', "")
                # Get rid of the split() when bug #67127 is fixed:
                # https://bugzilla.mozilla.org/show_bug.cgi?id=67127
                if '\n' in title:
                    title = title.split('\n')[0].strip()
                attrs['title'] = title
        elif tag == "meta":
            name = attrs.get_true('name', u'')
            if name.lower().startswith('x-rating'):
                name = name[8:]
                content = attrs.get_true('content', u'')
                self.rating[name] = content
        elif tag == "body":
            if self.ratings:
                # headers finished, check rating data
                # XXX what about a missing body tag?
                service = wc.configuration.config['rating_service']
                if "" not in self.rating or self.rating[""] != service.url:
                    raise wc.filter.FilterRating(_("No rating data found."))
                for rule in self.ratings:
                    service.rating_check(rule.rating, self.rating)
                self.ratings = []
        elif tag == "base":
            if attrs.has_key('href'):
                self.base_url = attrs['href']
                # some base urls are just the host name, eg. www.imadoofus.com
                if not urllib.splittype(self.base_url)[0]:
                    self.base_url = "%s://%s" % \
                               (urllib.splittype(self.url)[0], self.base_url)
                self.base_url = wc.url.url_norm(self.base_url)[0]
                assert None == wc.log.debug(wc.LOG_HTML,
                    "%s using base url %r", self, self.base_url)
        # search for and prevent known security flaws in HTML
        if self.security.scan_start_tag(tag, attrs, self):
        # remove this tag
            return
        # look for filter rules which apply
        self.filter_start_element(tag, attrs, starttype)
        # if rule stack is empty, write out the buffered data
        if not (self.rulestack or self.javascript):
            self.htmlparser.tagbuf2data()

    def get_tag_rules (self, tag):
        if tag not in self.rule_tag_cache:
            self.rule_tag_cache[tag] = \
                         [rule for rule in self.rules if rule.match_tag(tag)]
        return self.rule_tag_cache[tag]

    def filter_start_element (self, tag, attrs, starttype):
        """Filter the start element according to filter rules."""
        rulelist = []
        filtered = False
        item = [starttype, tag, attrs]
        for rule in self.get_tag_rules(tag):
            if rule.match_attrs(attrs):
                if rule.matches_starttag(tag):
                    item = rule.filter_tag(tag, attrs, starttype)
                    filtered = True
                elif not rule.contentmatch:
                    # If no contentmatch string has to be matched, this rule
                    # is a sure hit. Therefore set the filtered flag.
                    filtered = True
                if rule.matches_endtag(tag):
                    rulelist.append(rule)
                if item[0] == starttype and item[1] == tag:
                    # If both tag type and name did not change, more than one
                    # rule has a chance to replace data.
                    dummy, tag, attrs = item
                    continue
                else:
                    # If tag type or name changed, it's over.
                    break
        if rulelist:
            # Remember buffer position for end tag matching.
            pos = len(self.htmlparser.tagbuf)
            self.rulestack.append((pos, rulelist))
            self.stackcount.append([tag, 1])
        if filtered:
            # put filtered item on tag buffer
            self.htmlparser.tagbuf.append(item)
        elif self.javascript:
            # if it's not yet filtered, try filter javascript
            self.js_start_element(tag, attrs, starttype)
        else:
            # put original item on tag buffer
            self.htmlparser.tagbuf.append(item)

    def end_element (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
        If it matches and the rule stack is now empty we can flush
        the tag buffer (calling tagbuf2data).
        """
        assert None == wc.log.debug(wc.LOG_HTML,
            "%s end_element %r", self, tag)
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
        # don't write any data to buf if there are still rating rules
        if self.ratings:
            return
        if not self.rulestack:
            self.htmlparser.tagbuf2data()

    def filter_end_element (self, tag):
        """Filters an end tag, return True if tag was filtered, else
        False."""
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag) and \
           self.stackcount[-1][0] == tag and self.stackcount[-1][1] <= 0:
            del self.stackcount[-1]
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                mo = rule.match_complete(pos, self.htmlparser.tagbuf)
                if mo:
                    rule.filter_complete(pos, self.htmlparser.tagbuf, tag, mo)
                    return True
        return False
