# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Parse and filter ratings.
"""

from . import Filter, STAGE_RESPONSE_HEADER, FilterRating
from .. import configuration
from ..rating.service.rating import rating_from_headers


class Rating(Filter.Filter):
    """
    Reject pages that exceed the configured rating limit. Uses an
    existing rating store, as well as rating data supplied by
    X-Rating headers.
    Rating data in <meta> tags is handled by the HtmlRewriter filter
    and its HtmlFilter helper class.
    """

    enable = True

    def __init__(self):
        """
        Initialize image reducer flags.
        """
        stages = [STAGE_RESPONSE_HEADER]
        rulenames = ['rating']
        super(Rating, self).__init__(stages=stages, rulenames=rulenames)

    def doit(self, data, attrs):
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
        storage = configuration.config['rating_storage']
        service = configuration.config['rating_service']
        if url in storage:
            rating = storage[url].rating
            for rule in rules:
                service.rating_check(rule.rating, rating)
            return data
        erules = [r for r in rules if r.use_extern]
        if not erules:
            raise FilterRating(_("No rating data found."))
        headers = attrs['headers']['server']
        if 'X-Rating' in headers and headers['X-Rating'] == service.url:
            rating = rating_from_headers(headers)
            for rule in rules:
                service.rating_check(rule.rating, rating)
            return data
        if "HtmlRewriter" in configuration.config['filters']:
            # Wait for <meta> rating.
            return data
        raise FilterRating(_("No rating data found."))

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        Store rating rules in data.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(Rating, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        attrs['rating_rules'] = rules
