# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
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
Rating formats.
"""

import re
from .. import RatingFormat


class ValueFormat (RatingFormat):
    """
    Base class for formats that have three-valued range of
    "none", "mild" and "heavy".
    """

    def __init__ (self, name):
        """Initialize name and values."""
        _ = lambda x: x
        values = [_("none"), _("mild"), _("heavy")]
        del _
        super(ValueFormat, self).__init__(name, values)
        self.iterable = True

    def valid_value (self, value):
        """True if value is in values list."""
        return value in self.values

    def allowance (self, value, limit):
        """Check if value exceeds limit."""
        return self.values.index(value) <= self.values.index(limit)


class RangeFormat (RatingFormat):
    """
    Rating format that can hold values in a range between a given
    minimum and maximum.
    """

    def __init__ (self, name, intrange):
        """Initialize name and values."""
        super(RangeFormat, self).__init__(name, intrange)
        self.iterable = False

    def valid_value (self, value):
        """Check range value."""
        return self.values.contains_range(value)

    def allowance (self, value, limit):
        """Check if value exceeds limit."""
        return value.contains_range(limit)


class IntRange (object):

    def __init__ (self, minval=None, maxval=None):
        self.minval = minval
        self.maxval = maxval

    def contains_value (self, num):
        """Check if number is in range."""
        if num is None:
            return True
        isnum = isinstance(num, int) or isinstance(num, float)
        assert (isnum and num >= 0), "Invalid value %r" % repr(num)
        return (self.minval is None or num >= self.minval) and \
               (self.maxval is None or num <= self.maxval)

    def contains_range (self, intrange):
        """Check if given range lies in this range."""
        return self.contains_value(intrange.minval) and \
               self.contains_value(intrange.maxval)

    def __getitem__ (self, index):
        if index == 0:
            return self.minval
        if index == 1:
            return self.maxval
        raise IndexError("Invalid index")

    def __eq__ (self, other):
        return self.minval == other.minval and self.maxval == other.maxval

    def __str__ (self):
        s = ""
        if self.minval is not None:
            s += "%d-" % self.minval
        if self.maxval is not None:
            if not s:
                s += "-"
            s += "%d" % self.maxval
        return s

    def __repr__ (self):
        return "<IntRange min=%s max=%s>" % (self.minval, self.maxval)


_range_re = re.compile(r'^(\d*)-(\d*)$')
def parse_range (value):
    """
    Parse value as range.
    @return: parsed range object or None on error
    @rtype: IntRange or None
    """
    if not value:
        # empty range
        return IntRange()
    if value.isdigit():
        return IntRange(int(value), None)
    mo = _range_re.match(value)
    if not mo:
        return None
    vmin, vmax = mo.group(1), mo.group(2)
    if vmin == "":
        vmin = None
    else:
        vmin = max(int(vmin), 0)
    if vmax == "":
        vmax = None
    else:
        vmax = max(int(vmax), vmin)
    return IntRange(vmin, vmax)

