"""filter a HTML stream."""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

import re
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter import compileMime, compileRegex
from wc.filter.Filter import Filter
from wc.filter.HtmlParser import FilterHtmlParser
from wc.log import *


class Rewriter (Filter):
    """This filter can rewrite HTML tags. It uses a parser class."""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['rewrite', 'nocomments', 'javascript', 'pics']
    mimelist = [compileMime(x) for x in ['text/html']]

    def addrule (self, rule):
        super(Rewriter, self).addrule(rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")
        if rule.get_name()=='rewrite':
            compileRegex(rule, "enclosed")
            rule.attrs_ro = {}
            for key, val in rule.attrs.items():
                rule.attrs_ro[key] = re.compile(rule.attrs[key])


    def filter (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        p = attrs['filter']
        p.feed(data)
        return p.flushbuf()


    def finish (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        p = attrs['filter']
        # feed even if data is empty
        p.feed(data)
        p.flush()
        p.buf2data()
        return p.flushbuf()


    def getAttrs (self, headers, url):
        """We need a separate filter instance for stateful filtering"""
        rewrites = []
        pics = []
        # look if headers already have PICS label info
        opts = {'comments': True, 'javascript': False}
        for rule in self.rules:
            if not rule.appliesTo(url):
                continue
            if rule.get_name()=='rewrite':
                rewrites.append(rule)
            elif rule.get_name()=='nocomments':
                opts['comments'] = False
            elif rule.get_name()=='javascript':
                opts['javascript'] = True
            elif rule.get_name()=='pics':
                pics.append(rule)
        # generate the HTML filter
        return {'filter': FilterHtmlParser(rewrites, pics, url, **opts)}
