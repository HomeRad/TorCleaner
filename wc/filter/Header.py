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

import re
import sets

import wc
import wc.log
import wc.proxy.Headers
import wc.filter
import wc.filter.Filter


class Header (wc.filter.Filter.Filter):
    """filter for adding, modifying and deleting headers"""

    # which filter stages this filter applies to (see filter/__init__.py)
    stages = [wc.filter.STAGE_REQUEST_HEADER,
              wc.filter.STAGE_RESPONSE_HEADER]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['header']
    # which mime types this filter applies to
    mimelist = []

    def get_attrs (self, url, stage, headers):
        """configure header rules to add/delete"""
        d = super(Header, self).get_attrs(url, stage, headers)
        delete = []
        add = []
        for rule in self.rules:
            # filter out unwanted rules
            if not rule.applies_to(url) or not rule.name:
                continue
            # name is a regular expression match object
            if not rule.value:
                # no value --> header name should be deleted
                # deletion can apply to many headers
                matcher = re.compile(rule.name, re.I).match
                if rule.filterstage in ('both', stage):
                    delete.append(matcher)
            else:
                # name, value must be ASCII strings
                name = str(rule.name)
                val = str(rule.value)
                if rule.filterstage in ('both', stage):
                    add.append((name, val))
        d['header_add'] = add
        d['header_delete'] = delete
        return d

    def doit (self, data, attrs):
        """apply stored header rules to data, which is a WcMessage object"""
        wc.log.debug(wc.LOG_FILTER, "%s filter %s", self, data)
        delete = sets.Set()
        # stage is STAGE_REQUEST_HEADER or STAGE_RESPONSE_HEADER
        for h in data.keys():
            for name_match in attrs['header_delete']:
                if name_match(h):
                    wc.log.debug(wc.LOG_FILTER,
                                 "%s removing header %r", self, h)
                    delete.add(h.lower())
                    # go to next header name
                    break
        wc.proxy.Headers.remove_headers(data, delete)
        for name, val in attrs['header_add']:
            wc.log.debug(wc.LOG_FILTER,
                         "%s adding header %r: %r", self, name, val)
            data[name] = val+"\r"
        return data
