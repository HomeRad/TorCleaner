# -*- coding: iso-8859-1 -*-
"""Rating class."""
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

class Rating (object):
    """A single rating applies to a given URL and specifies a list
       of categories with their associated value.
       Generic ratings apply to all URLs starting with the given URL.
    """

    def __init__ (self, url, generic):
        """Initialize url and generic flag. Set category values to
           an empty map."""
        self.url = url
        self.category_values = {}
        self.generic = generic

    def add_category_value (self, category, value):
        self.category_values[category] = value

    def delete_category (self, category):
        if category in self.category_values:
            del self.category_values[category]

