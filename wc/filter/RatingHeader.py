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

import wc.filter
import wc.filter.Filter
import wc.filter.Rating
import wc.log


class RatingHeader (wc.filter.Filter.Filter):
    """Adds rating data supplied in 'Content-Rating' headers"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_HEADER,]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['rating']
    # applies to all mime types
    mimelist = []

    def doit (self, data, **attrs):
        url = attrs['url']
        headers = attrs['headers']['server']
        if headers.has_key('Content-Rating'):
            cached_rating = wc.filter.Rating.rating_cache_get(url)
            if cached_rating is None:
                rating = headers['Content-Rating']
                try:
                    url, rating = wc.filter.Rating.rating_import(url, rating)
                    wc.filter.Rating.rating_add(url, rating)
                except wc.filter.Rating.RatingParseError, msg:
                    wc.log.warn(wc.LOG_FILTER, "rating parse error: %s", msg)
        rules = attrs['rating_rules']
        for rule in rules:
            msg = wc.filter.Rating.rating_allow(url, rule)
            if msg:
                raise wc.filter.FilterRating(msg)
        return data


    def get_attrs (self, url, headers):
        d = super(RatingHeader, self).get_attrs(url, headers)
        # weed out the rules that don't apply to this url
        d['rating_rules'] = [ rule for rule in self.rules if rule.appliesTo(url) ]
        return d
