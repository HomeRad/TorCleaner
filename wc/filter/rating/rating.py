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
Rating class.
"""

import time
import wc.filter.rating
import wc.filter.rating.category

class Rating (object):
    """
    A single rating applies to a given URL and specifies a list
    of categories with their associated value.
    Generic ratings apply to all URLs starting with the given URL.
    """

    def __init__ (self, url, generic):
        """
        Initialize url and generic flag. Set category values to
        an empty map and modified time to now.
        """
        self.url = url
        self.category_values = {}
        self.generic = generic
        self.modified = time.time()

    def add_category_value (self, category, value):
        """
        Add value for given category. Updates modified time.
        """
        assert category.valid_value(value), \
          "Invalid value %s for category %s" % (repr(value), str(category))
        self.category_values[category.name] = value
        self.modified = time.time()

    def remove_category (self, category):
        """
        Remove given category. Updates modified time.
        """
        if category.name in self.category_values:
            del self.category_values[category.name]
            self.modified = time.time()

    def remove_categories (self):
        """
        Remove all categories. Updates modified time.
        """
        if self.category_values:
            self.category_values = {}
            self.modified = time.time()

    def serialize (self):
        """
        Return serialized string of this rating.
        """
        lines = []
        lines.append("url %s" % self.url)
        lines.append("generic %s" % str(self.generic))
        lines.append("modified %d" % self.modified)
        for name, value in self.category_values.items():
            category = wc.filter.rating.get_category(name)
            if not category.iterable:
                value = wc.filter.rating.category.string_from_intrange(value)
            lines.append("category %s=%s" % (name, value))
        return "\n".join(lines)
