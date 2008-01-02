# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2008 Bastian Kleineidam
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
For each templates/<theme>/<file>.html there is a context/<file>_html.py
module delivering the page content values.
"""

import re

charset = 'iso-8859-1'

def get_item_value (item):
    """
    Return a plain value of the given form field item.
    """
    if isinstance(item, list):
        value = item[0]
    elif hasattr(item, "value"):
        value = item.value
    else:
        value = item
    return value.decode(charset)


def get_item_list (item):
    """
    Return a plain value of the given form field item.
    """
    if isinstance(item, list):
        value = [get_item_value(x) for x in item]
    elif hasattr(item, "value"):
        value = [item.value.decode(charset)]
    else:
        value = [item.decode(charset)]
    return value


def getval (form, key):
    """
    Return a formfield value.
    """
    if not form.has_key(key):
        return u''
    return get_item_value(form[key])


def getlist (form, key):
    """
    Return a list of formfield values.
    """
    if not form.has_key(key):
        return []
    return get_item_list(form[key])


def get_prefix_vals (form, prefix):
    """
    Return a list of (key, value) pairs where ``prefix+key'' is a valid
    form field.
    """
    res = []
    for key in form:
        if key.startswith(prefix):
            res.append((key[len(prefix):], get_item_value(form[key])))
    return res


is_safe = re.compile(r"^[a-zA-Z0-9 ]$").match
def filter_safe (text):
    """
    Safe whitelist quoting for html content.
    """
    return u"".join([c for c in text if is_safe(c)])
