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

import wc.filter
import wc.filter.Filter
import wc.filter.html.HtmlParser
import wc.filter.html.HtmlFilter


DefaultCharset = 'iso-8859-1'

class HtmlRewriter (wc.filter.Filter.Filter):
    """
    This filter can rewrite HTML tags. It uses a parser class.
    """

    enable = True

    def __init__ (self):
        """
        Init stages and mimes.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ['htmlrewrite', 'nocomments', 'javascript', 'rating']
        mimes = ['text/html']
        super(HtmlRewriter, self).__init__(stages=stages, rulenames=rulenames,
                                       mimes=mimes)

    def filter (self, data, attrs):
        """
        Feed data to HTML parser.
        """
        if not attrs.has_key('htmlrewriter_filter'):
            return data
        p = attrs['htmlrewriter_filter']
        p.feed(data)
        if p.handler.ratings:
            # XXX correct raise
            raise wc.filter.FilterWait, "wait for rating decision"
        if p.bom is not None:
            bom, p.bom = p.bom, None
            return bom + p.getoutput()
        return p.getoutput()

    def finish (self, data, attrs):
        """
        Feed data to HTML parser and flush buffers.
        """
        if not attrs.has_key('htmlrewriter_filter'):
            return data
        p = attrs['htmlrewriter_filter']
        # feed even if data is empty
        p.feed(data)
        # flushing can raise FilterWait exception
        p.flush()
        if p.handler.ratings:
            # XXX correct raise
            raise wc.filter.FilterRating, "missing rating"
        p.tagbuf2data()
        return p.getoutput()

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        We need a separate filter instance for stateful filtering.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(HtmlRewriter, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        rewrites = []
        ratings = []
        # look if headers already have rating info
        opts = {'comments': True, 'jscomments': True, 'javascript': False}
        for rule in self.rules:
            if not rule.applies_to_url(url):
                continue
            if rule.name == 'htmlrewrite':
                rewrites.append(rule)
            elif rule.name == 'nocomments':
                opts['comments'] = False
            elif rule.name == 'nojscomments':
                opts['jscomments'] = False
            elif rule.name == 'javascript':
                opts['javascript'] = True
            elif rule.name == 'rating':
                ratings.append(rule)
        # generate the HTML filter
        handler = wc.filter.html.HtmlFilter.HtmlFilter(rewrites, ratings,
                                                       url, localhost, **opts)
        p = wc.filter.html.HtmlParser.HtmlParser(handler)
        #htmlparser.debug(1)
        # the handler is modifying parser buffers and state
        handler.htmlparser = p
        attrs['htmlrewriter_filter'] = p
