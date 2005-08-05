# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
Numeric constants for XML/HTML document parts.
"""

# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
STARTENDTAG = 4

# tag part ids
TAG = 0        # the tag inclusive the <>
TAGNAME = 1    # the tag name
ATTR = 2       # a complete attribute
ATTRVAL = 3    # attribute value
ATTRNAME = 4   # attribute name
COMPLETE = 5   # start/end tag and content
ENCLOSED = 6   # only enclosed content
