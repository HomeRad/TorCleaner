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
Basic data types and routines for rating support.
"""

import wc.decorators
import wc.containers

class Rating (wc.containers.CaselessSortedDict):
    """
    A rating is a dictionary filled with name/value items.
    Each name/value item is an instance of a defined rating format.
    """
    pass


class RatingFormat (object):
    """
    A rating format defines a unique, case insensitive name, and a range
    of valid values along with their interpretation.
    """

    def __init__ (self, name, values):
        self.name = name
        self.values = values

    @wc.decorators.notimplemented
    def valid_value (self, value):
        """True if value is valid according to this format."""
        pass

    @wc.decorators.notimplemented
    def allowance (self, value, limit):
        """Check if value exceeds limit according to this format."""
        pass

    def __str__ (self):
        args = (self.__class__.__name__, self.name, str(self.values))
        return "%s %r: %s" % args


class UrlRating (object):
    """
    A URL rating relates a rating to one or more URLs. It consists of
    a rating, an URL and an optional generic flag specifying that all
    URLs with the given URL as base path apply to the rating.
    """

    def __init__ (self, url, rating, generic=False):
        self.url = url
        self.rating = rating
        self.generic = generic


class RatingService (object):
    """
    A rating service defines a unique name and the (sub-)set of supported
    rating formats. The service name should be an URL with human-viewable
    information about the service.

    The service should store and/or deliver URL ratings of the formats it
    defines.
    """

    def __init__ (self, url, rating_formats):
        self.url = url
        self.rating_formats = rating_formats

    @wc.decorators.notimplemented
    def get_url_rating (self, url):
        pass

    @wc.decorators.notimplemented
    def set_url_rating (self, url, rating, generic):
        pass
