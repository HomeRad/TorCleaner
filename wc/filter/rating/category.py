# -*- coding: iso-8859-1 -*-
"""Rating categories."""
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

class Category (object):
    """A rating category has a name and an object describing what
       values it can hold.
    """

    def __init__ (self, name, values):
        """Initialize name and values."""
        self.name = name
        self.values = values

    def valid_value (self, value):
        """True if value is valid according to this category."""
        raise NotImplementedError, "unimplemented"


class ValueCategory (Category):
    """Rating category that can hold the discrete values none, mild,
       heavy."""

    def __init__ (self, name):
        """Initialize name and values."""
        _ = lambda x: x
        values = [_("none"), _("mild"), _("heavy")]
        del _
        super(ValueCategory, self).__init__(name, values)

    def valid_value (self, value):
        """True if value is in values list."""
        return value in self.values


class RangeCategory (Category):
    """Rating category that can hold values in a range between a given
       minimum and maximum.
    """

    def __init__ (self, name, minval=None, maxval=None):
        """Initialize name and values."""
        super(RangeCategory, self).__init__(name, [minval, maxval])

    def valid_value (self, value):
        """Check range value."""
        if not isinstance(value, tuple):
            return value_in_range(value, self.values)
        assert len(value) == 2, "Invalid value %r" % repr(value)
        return range_in_range(value, self.values)


def value_in_range (num, prange):
    """return True iff number is in range.
       prange - tuple (min, max)
       value - a number
    """
    if prange[0] is not None and num is not None and num < prange[0]:
        return False
    if prange[1] is not None and num is not None and num > prange[1]:
        return False
    return True


def range_in_range (vrange, prange):
    """return True iff num vrange is in prange.
       prange - tuple (min, max)
       vrange - tuple (min, max)
    """
    return value_in_range(vrange[0], prange) and \
           value_in_range(vrange[1], prange)

