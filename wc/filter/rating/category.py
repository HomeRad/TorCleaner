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


class ValueCategory (Category):
    """Rating category that can hold the discrete values none, mild,
       heavy."""

    def __init__ (self, name):
        """Initialize name and values."""
        _ = lambda x: x
        values = [_("none"), _("mild"), _("heavy")]
        del _
        super(ValueCategory, self).__init__(name, values)


class RangeCategory (Category):
    """Rating category that can hold values in a range between a given
       minimum and maximum.
    """

    def __init__ (self, name, minval=None, maxval=None):
        """Initialize name and values."""
        super(RangeCategory, self).__init__(name, [minval, maxval])

