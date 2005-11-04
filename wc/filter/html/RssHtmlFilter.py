# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
A HTML filter that only allows a safe tag subset, suitable for displaying
in an RSS reader.
"""

from StringIO import StringIO

import wc
import wc.log
import wc.HtmlParser.htmllib
import wc.HtmlParser.htmlsax

# allowed HTML tags with their attributes
rss_allowed = {
    u"a": [u"href"],
    u"div": [],
    u"span": [],
    u"br": [u"clear"],
    u"hr": [],
    u"p": [],
    u"img": [u"src", u"width", u"height", u"alt", u"title", u"border", u"align", u"vspace", u"hspace"],
    u"b": [],
    u"strong": [],
    u"em": [],
    u"i": [],
    u"code": [],
    u"sub": [],
    u"sup": [],
    u"blockquote": [],
    u"cite": [],
    u"table": [],
    u"tbody": [],
    u"thead": [],
    u"tfoot": [],
    u"ul": [],
    u"ol": [],
    u"li": [],
    u"tr": [u"align"],
    u"th": [u"align"],
    u"td": [u"align", u"colspan", u"rowspan"],
}
# HTML tags with attributes holding URIs
rss_uris = {
    u"a": [u"href"],
    u"img": [u"src"],
}

class RssHtmlFilter (object):

    def __init__ (self):
        self.parser = wc.HtmlParser.htmlsax.parser(self)
        self.reset()

    def reset (self):
        self.outbuf = StringIO()
        self.url = ""
        self.valid = True
        self.stack = []
        self.rules = []

    def filter (self, data, url, rules):
        # XXX remove encoding when HTML parser supports unicode
        encoding = "iso8859-1"
        self.parser.encoding = encoding
        data = data.encode(encoding, "ignore")
        self.rules = rules
        self.url = url
        self.parser.feed(data)
        self.parser.flush()
        self.parser.reset()
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.reset()
        return data

    def __repr__ (self):
        """
        Representation with recursion level and state.
        """
        return "<RssHtmlFilter %s>" % self.url

    def _data (self, data):
        """
        General handler for data.
        """
        if self.valid:
            self.outbuf.write(data)

    def cdata (self, data):
        """
        Character data.
        """
        return self._data(data)

    def characters (self, data):
        """
        Characters.
        """
        return self._data(data)

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
        tag = wc.filter.html.check_spelling(tag, self.url)
        self.stack.append(tag)
        if not self.valid:
            return
        if tag in rss_allowed:
            self.outbuf.write(u"<%s" % tag)
            if attrs:
                quote = wc.HtmlParser.htmllib.quote_attrval
                for attr in attrs:
                    if attr in rss_allowed[tag]:
                        val = attrs[attr]
                        self.outbuf.write(u' %s="%s"' % (attr, quote(val)))
            if startend:
                self.outbuf.write(u"/>")
            else:
                self.outbuf.write(u">")
        elif not startend:
            self.valid = False
            self.stack = [tag]

    def end_element (self, tag):
        tag = wc.filter.html.check_spelling(tag, self.url)
        if self.stack and self.stack[-1] == tag:
            del self.stack[-1]
        if self.valid:
            self.outbuf.write(u"</%s>" % tag)
        else:
            self.valid = not self.stack
