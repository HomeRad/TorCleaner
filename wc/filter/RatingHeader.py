# -*- coding: iso-8859-1 -*-
"""Parse and filter ratings.
"""
# Copyright (C) 2004  Bastian Kleineidam
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

from wc.log import *
from wc.filter.Filter import Filter
from wc.filter import FILTER_RESPONSE_HEADER, FilterRating
from wc.filter.Rating import rating_cache_get, rating_add, rating_allow, rating_import, RatingParseError

class RatingHeader (Filter):
    """Adds rating data supplied in 'Content-Rating' headers"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_HEADER,]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['rating']
    # applies to all mime types
    mimelist = []

    def doit (self, data, **attrs):
        url = attrs['url']
        headers = attrs['headers']
        if headers.has_key('Content-Rating'):
            cached_rating = rating_cache_get(url)
            if cached_rating is None:
                rating = headers['Content-Rating']
                try:
                    url, rating = rating_import(url, rating)
                    rating_add(url, rating)
                except RatingParseError, msg:
                    warn(FILTER, "rating parse error: %s", msg)
        rules = attrs['rating_rules']
        for rule in rules:
            msg = rating_allow(url, rule)
            if msg:
                raise FilterRating(msg)
        return data


    def getAttrs (self, url, headers):
        d = super(RatingHeader, self).getAttrs(url, headers)
        # weed out the rules that don't apply to this url
        d['rating_rules'] = [ rule for rule in self.rules if rule.appliesTo(url) ]
        return d
