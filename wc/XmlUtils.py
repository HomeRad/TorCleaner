# -*- coding: iso-8859-1 -*-
"""XML utility functions"""
# Copyright (C) 2003-2005  Bastian Kleineidam
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

import xml.sax.saxutils

attr_entities = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
}


def xmlquote (s):
    """quote characters for XML"""
    return xml.sax.saxutils.escape(s)


def xmlquoteattr (s):
    """quote XML attribute, ready for inclusion with double quotes"""
    return xml.sax.saxutils.escape(s, attr_entities)


def xmlunquote (s):
    """unquote characters from XML"""
    return xml.sax.saxutils.unescape(s)


def xmlunquoteattr (s):
    """unquote attributes from XML"""
    return xml.sax.saxutils.unescape(s, attr_entities)
