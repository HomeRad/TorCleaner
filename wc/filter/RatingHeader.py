# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Parse and filter ratings.
"""

import wc.filter
import wc.filter.Filter
import wc.filter.rating
import wc.log


class RatingHeader (wc.filter.Filter.Filter):
    """
    Adds rating data supplied in 'Content-Rating' headers.
    """

    enable = True

    def __init__ (self):
        """
        Initialize image reducer flags.
        """
        stages = [wc.filter.STAGE_RESPONSE_HEADER]
        rulenames = ['rating']
        super(RatingHeader, self).__init__(stages=stages, rulenames=rulenames)

    def doit (self, data, attrs):
        """
        Parse and check Content-Rating header according to rating rules.

        @return: data
        @rtype: string
        @raise: FilterRating when page is rated too high
        """
        url = attrs['url']
        headers = attrs['headers']['server']
        if headers.has_key('Content-Rating'):
            cached_rating = wc.filter.rating.rating_cache_get(url)
            if cached_rating is None:
                rating = headers['Content-Rating']
                try:
                    url, rating = wc.filter.rating.rating_import(url, rating)
                    wc.filter.rating.rating_add(url, rating)
                except wc.filter.rating.RatingParseError, msg:
                    wc.log.warn(wc.LOG_FILTER, "rating parse error: %s", msg)
        rules = attrs['rating_rules']
        for rule in rules:
            msg = rule.rating_allow(url)
            if msg:
                assert wc.log.debug(wc.LOG_FILTER, "rated page: %s", msg)
                raise wc.filter.FilterRating, msg
        return data

    def get_attrs (self, url, localhost, stages, headers):
        """
        Store rating rules in data.
        """
        if not self.applies_to_stages(stages):
            return {}
        d = super(RatingHeader, self).get_attrs(url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        d['rating_rules'] = [rule for rule in self.rules if \
                             rule.applies_to_url(url)]
        return d
