# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Basic data types and routines for rating support.
"""

from .. import decorators, containers

class Rating(containers.CaselessSortedDict):
    """
    A rating is a dictionary filled with name/value items.
    Each name/value item is an instance of a defined rating format.
    """
    pass


class RatingFormat(object):
    """
    A rating format defines a unique, case insensitive name, and a range
    of valid values along with their interpretation.
    """

    def __init__(self, name, values):
        self.name = name
        self.values = values

    @decorators.notimplemented
    def valid_value(self, value):
        """True if value is valid according to this format."""
        pass

    @decorators.notimplemented
    def allowance(self, value, limit):
        """Check if value exceeds limit according to this format."""
        pass

    def __str__(self):
        args = (self.__class__.__name__, self.name, str(self.values))
        return "%s %r: %s" % args


class UrlRating(object):
    """
    A URL rating relates a rating to one or more URLs. It consists of
    a rating, an URL and an optional generic flag specifying that all
    URLs with the given URL as base path apply to the rating.
    """

    def __init__(self, url, rating, generic=False):
        self.url = url
        self.rating = rating
        self.generic = generic


class RatingService(object):
    """
    A rating service defines a unique name and the (sub-)set of supported
    rating formats. The service name should be an URL with human-viewable
    information about the service.

    The service should store and/or deliver URL ratings of the formats it
    defines.
    """

    def __init__(self, url, rating_formats):
        self.url = url
        self.rating_formats = rating_formats

    @decorators.notimplemented
    def get_url_rating(self, url):
        pass

    @decorators.notimplemented
    def set_url_rating(self, url, rating, generic):
        pass
