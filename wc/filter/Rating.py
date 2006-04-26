# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
import wc.rating
import wc.log
from wc.rating.service.rating import rating_from_headers, rating_check_rules


class Rating (wc.filter.Filter.Filter):
    """
    Reject pages that exceed the configured rating limit. Uses an
    existing rating store, as well as rating data supplied by
    X-Rating headers.
    Rating data in <meta> tags is handled by the HtmlRewriter filter
    and its HtmlFilter helper class.
    """

    enable = True

    def __init__ (self):
        """Initialize image reducer flags."""
        stages = [wc.filter.STAGE_RESPONSE_HEADER]
        rulenames = ['rating']
        super(Rating, self).__init__(stages=stages, rulenames=rulenames)

    def doit (self, data, attrs):
        """
        Parse and check Content-Rating header according to rating rules.

        @return: data
        @rtype: string
        @raise: FilterRating when page is rated too high
        """
        rules = attrs['rating_rules']
        if not rules:
            return data
        url = attrs['url']
        config = wc.configuration.config
        storage = config['rating_storage']
        service = config['rating_service']
        if url in storage:
            rating = storage[url].rating
            if not rating_check_rules(service, rules, rating):
                raise wc.filter.FilterRating(url)
            return data
        erules = [r for r in rules if r.use_extern]
        if not erules:
            raise wc.filter.FilterRating(url)
        headers = attrs['headers']['server']
        if headers.has_key('X-Rating') and headers['X-Rating'] == service.url:
            try:
                rating = rating_from_headers(headers)
                if not rating_check_rules(service, rules, rating):
                    raise wc.filter.FilterRating(url)
            except wc.rating.RatingParseError, msg:
                wc.log.warn(wc.LOG_FILTER, "rating parse error: %s", msg)
        if "HtmlRewriter" in config['filters']:
            # Wait for <meta> rating.
            return data
        raise wc.filter.FilterRating(url)

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """Store rating rules in data."""
        if not self.applies_to_stages(stages):
            return
        parent = super(Rating, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        attrs['rating_rules'] = rules
