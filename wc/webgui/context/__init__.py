# -*- coding: iso-8859-1 -*-
"""for each template/<theme>/<file>.html there is a context/<file>_html.py
module delivering the page content values"""
# Copyright (C) 2003-2004  Bastian Kleineidam
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

import re

def getval (form, key):
    """return a formfield value"""
    if not form.has_key(key):
        return ''
    item = form[key]
    if isinstance(item, list):
        return item[0]
    if hasattr(item, "value"):
        return item.value
    return item


def getlist (form, key):
    """return a list of formfield values"""
    if not form.has_key(key):
        return []
    item = form[key]
    if isinstance(item, list):
        return [x.value for x in item]
    if hasattr(item, "value"):
        return [item.value]
    return [item]


is_safe = re.compile(r"^[a-zA-Z0-9 ]$").match
def filter_safe (text):
    """safe whitelist quoting for html content"""
    return "".join([c for c in text if is_safe(c)])
