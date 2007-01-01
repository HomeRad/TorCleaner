# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2007 Bastian Kleineidam
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
Filter invalid binary chars from HTML.
"""

import string
import re
import wc.filter
import Filter

# for utf charset check (see below)
is_utf = re.compile(r"text/html;\s*charset=utf-8", re.I).search

# character replacement table.
charmap = (
    # Replace Null byte with space
    (chr(0x0), chr(0x20)),  # ' '
    # Replace Microsoft quotes
    (chr(0x84), chr(0x22)), # '"'
    (chr(0x91), chr(0x60)), # '`'
    (chr(0x92), chr(0x27)), # '\''
    (chr(0x93), chr(0x22)), # '"'
    (chr(0x94), chr(0x22)), # '"'
)
charmap_in = ''.join(x[0] for x in charmap)
charmap_out = ''.join(x[1] for x in charmap)


class BinaryCharFilter (Filter.Filter):
    """
    Replace binary characters, often found in Microsoft HTML documents,
    with their correct HTML equivalent.
    """

    enable = True

    def __init__ (self):
        """
        Initialize stages and mime list.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        mimes = ['text/html']
        super(BinaryCharFilter, self).__init__(stages=stages, mimes=mimes)
        self.transe = string.maketrans(charmap_in, charmap_out)

    def doit (self, data, attrs):
        """
        Filter given data.
        """
        # The HTML parser does not yet understand Unicode, so this hack
        # disables the binary char filter in this case.
        if is_utf(data):
            attrs['charset'] = "utf-8"
        if attrs.get('charset') == "utf-8":
            return data
        return data.translate(self.transe)
