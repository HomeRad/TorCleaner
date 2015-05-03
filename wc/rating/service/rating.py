# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2009 Bastian Kleineidam
"""
Rating import and export to various formats.
"""

from .. import Rating


def rating_from_headers(headers):
    """
    Parse X-Rating-* HTTP headers into a rating dictionary.
    @param headers: server headers
    @ptype headers: wc.http.header.WcMessage
    @return: parsed rating
    @rtype: wc.rating.Rating
    """
    rating = Rating()
    for name, value in headers:
        if name.lower().startswith("x-rating-"):
            rating[name[9:]] = value
    return rating
