"""XML utility functions"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

# standard xml entities
xmlentities = {
    'lt': '<',
    'gt': '>',
    'amp': '&',
    'quot': '"',
    'apos': "'",
}

_xml_table = map(lambda x: (x[1], "&"+x[0]+";"), xmlentities.items())
_unxml_table = map(lambda x: ("&"+x[0]+";", x[1]), xmlentities.items())
# order matters!
_xml_table.sort()
_unxml_table.sort()
_unxml_table.reverse()

def _apply_table (table, s):
    "apply a table of replacement pairs to str"
    for mapping in table:
        s = s.replace(mapping[0], mapping[1])
    return s

def xmlify (s):
    """quote characters for XML"""
    return _apply_table(_xml_table, s)

def unxmlify (s):
    """unquote characterx from XML"""
    return _apply_table(_unxml_table, s)

