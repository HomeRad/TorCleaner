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
Rating formats.
"""

import re
import wc.rating


class ValueFormat (wc.rating.RatingFormat):
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
        return self.values.index(value) > self.values.index(limit)


class RangeFormat (wc.rating.RatingFormat):
    """
    Rating format that can hold values in a range between a given
    minimum and maximum.
    """

    def __init__ (self, name, minval=None, maxval=None):
        """Initialize name and values."""
        super(RangeFormat, self).__init__(name, [minval, maxval])
        self.iterable = False

    def valid_value (self, value):
        """Check range value."""
        return range_check(value, self.values)

    def allowance (self, value, limit):
        """Check if value exceeds limit."""
        return range_check(value, limit)


def range_check (value, values):
    if isinstance(value, tuple):
        assert len(value) == 2, "Invalid value %r" % repr(value)
        return range_in_range(value, values)
    return value_in_range(value, values)


def value_in_range (num, prange):
    """
    return True iff number is in range.

    @param prange: tuple (min, max)
    @param value: a number
    """
    isnum = isinstance(num, int) or isinstance(num, float)
    assert num is None or (isnum and num >= 0), "Invalid value %r" % repr(num)
    if prange[0] is not None and num is not None and num < prange[0]:
        return False
    if prange[1] is not None and num is not None and num > prange[1]:
        return False
    return True


def range_in_range (vrange, prange):
    """
    return True iff num vrange is in prange.

    @param prange: tuple (min, max)
    @param vrange: tuple (min, max)
    """
    return value_in_range(vrange[0], prange) and \
           value_in_range(vrange[1], prange)


_range_re = re.compile(r'^(\d*)-(\d*)$')
def intrange_from_string (value):
    """
    Parse value as range.
    @return: tuple (rmin, rmax) or None on error
    @rtype: tuple (int/None, int/None)
    """
    if not value:
        # empty range
        return (None, None)
    if value.isdigit():
        return (int(value), None)
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
    return (vmin, vmax)


def string_from_intrange (vrange):
    """
    Represent vrange as string.
    """
    s = ""
    if vrange[0]:
        s += "%d-" % vrange[0]
    if vrange[1]:
        if not s:
            s += "-"
        s += "%d" % vrange[1]
    return s
