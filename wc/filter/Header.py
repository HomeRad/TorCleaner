# -*- coding: iso-8859-1 -*-
"""webcleaner module: add or delete HTTP headers"""
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
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_REQUEST_HEADER, FILTER_RESPONSE_HEADER]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['header']
    mimelist = []

    def __init__ (self):
        super(Header, self).__init__()
        self.delete = []
        self.add = {}


    def addrule (self, rule):
        super(Header, self).addrule(rule)
        # ignore empty rules
        if not rule.name:
            return
        if not rule.value:
            self.delete.append(rule.name.lower())
        else:
            self.add[rule.name] = rule.value


    def doit (self, data, **args):
        delete = {}
        for h in data.keys():
            for name in self.delete:
                if re.match(name, h):
                    delete[h.lower()] = h
        remove_headers(data, delete.values())
        for key,val in self.add.items():
            data[key] = val+"\r"
        return data
