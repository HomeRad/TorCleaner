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
import wc.filter.HtmlParser
import wc.filter.HtmlFilter


DefaultCharset = 'iso-8859-1'

class Rewriter (wc.filter.Filter.Filter):
    """
    This filter can rewrite HTML tags. It uses a parser class.
    """

    def __init__ (self):
        """
        Init stages and mimes.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ['rewrite', 'nocomments', 'javascript', 'rating']
        mimes = ['text/html']
        super(Rewriter, self).__init__(stages=stages, rulenames=rulenames,
                                       mimes=mimes)

    def filter (self, data, attrs):
        if not attrs.has_key('rewriter_filter'):
            return data
        p = attrs['rewriter_filter']
        p.feed(data)
        if p.handler.ratings:
            # XXX correct raise
            raise wc.filter.FilterWait, "wait for rating decision"
        return p.getoutput()

    def finish (self, data, attrs):
        if not attrs.has_key('rewriter_filter'):
            return data
        p = attrs['rewriter_filter']
        # feed even if data is empty
        p.feed(data)
        # flushing can raise FilterWait exception
        p.flush()
        if p.handler.ratings:
            # XXX correct raise
            raise wc.filter.FilterRating, "missing rating"
        p.tagbuf2data()
        return p.getoutput()

    def get_attrs (self, url, localhost, stages, headers):
        """
        We need a separate filter instance for stateful filtering.
        """
        if not self.applies_to_stages(stages):
            return {}
        d = super(Rewriter, self).get_attrs(url, localhost, stages, headers)
        rewrites = []
        ratings = []
        # look if headers already have rating info
        opts = {'comments': True, 'javascript': False}
        for rule in self.rules:
            if not rule.applies_to(url):
                continue
            if rule.get_name() == 'rewrite':
                rewrites.append(rule)
            elif rule.get_name() == 'nocomments':
                opts['comments'] = False
            elif rule.get_name() == 'javascript':
                opts['javascript'] = True
            elif rule.get_name() == 'rating':
                ratings.append(rule)
        # generate the HTML filter
        handler = wc.filter.HtmlFilter.HtmlFilter(rewrites, ratings,
                                                  url, localhost, **opts)
        p = wc.filter.HtmlParser.HtmlParser(handler)
        #htmlparser.debug(1)
        # the handler is modifying parser buffers and state
        handler.htmlparser = p
        d['rewriter_filter'] = p
        return d
