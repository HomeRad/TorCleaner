# -*- coding: iso-8859-1 -*-
"""add or delete HTTP headers"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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
from wc.proxy.Headers import remove_headers
from wc.filter import FILTER_REQUEST_HEADER, FILTER_RESPONSE_HEADER
from wc.filter.Filter import Filter


class Header (Filter):
    """filter for adding, modifying and deleting headers"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_REQUEST_HEADER, FILTER_RESPONSE_HEADER]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['header']
    mimelist = []

    def __init__ (self):
        """initalize filter delete/add lists"""
        super(Header, self).__init__()
        self.delete = {
            FILTER_REQUEST_HEADER: [],
            FILTER_RESPONSE_HEADER: [],
        }
        self.add = {
            FILTER_REQUEST_HEADER: {},
            FILTER_RESPONSE_HEADER: {},
        }


    def addrule (self, rule):
        """add given rule to filter, filling header delete/add lists"""
        super(Header, self).addrule(rule)
        # ignore empty rules
        if not rule.name:
            return
        if not rule.value:
            if rule.filterstage in ('both', 'request'):
                self.delete[FILTER_REQUEST_HEADER].append(rule.name.lower())
            if rule.filterstage in ('both', 'response'):
                self.delete[FILTER_RESPONSE_HEADER].append(rule.name.lower())
        else:
            if rule.filterstage in ('both', 'request'):
                self.add[FILTER_REQUEST_HEADER][rule.name] = rule.value
            if rule.filterstage in ('both', 'response'):
                self.add[FILTER_RESPONSE_HEADER][rule.name] = rule.value


    def doit (self, data, **attrs):
        """apply stored header rules to data, which is a WcMessage object"""
        delete = {}
        # stage is FILTER_REQUEST_HEADER or FILTER_RESPONSE_HEADER
        stage = attrs['filterstage']
        for h in data.keys():
            for name in self.delete[stage]:
                if re.match(name, h):
                    delete[h.lower()] = h
        remove_headers(data, delete.values())
        for key,val in self.add[stage].items():
            data[key] = val+"\r"
        return data
