# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
Add or delete HTTP headers.
"""

import re
import sets

import wc
import wc.log
import wc.proxy.Headers
import wc.filter
import wc.filter.Filter


class Header (wc.filter.Filter.Filter):
    """
    Filter for adding, modifying and deleting headers.
    """

    def __init__ (self):
        """
        Init stages and rulenames.
        """
        stages = [wc.filter.STAGE_REQUEST_HEADER,
                  wc.filter.STAGE_RESPONSE_HEADER]
        rulenames = ['header']
        super(Header, self).__init__(stages=stages, rulenames=rulenames)

    def get_attrs (self, url, localhost, stages, headers):
        """
        Configure header rules to add/delete.
        """
        if not self.applies_to_stages(stages):
            return {}
        d = super(Header, self).get_attrs(url, localhost, stages, headers)
        delete = {
            wc.filter.STAGE_REQUEST_HEADER: [],
            wc.filter.STAGE_RESPONSE_HEADER: [],
        }
        add = {
            wc.filter.STAGE_REQUEST_HEADER: [],
            wc.filter.STAGE_RESPONSE_HEADER: [],
        }
        for rule in self.rules:
            # filter out unwanted rules
            if not rule.applies_to(url) or not rule.name:
                continue
            # name is a regular expression match object
            if not rule.value:
                # no value --> header name should be deleted
                # deletion can apply to many headers
                matcher = re.compile(rule.name, re.I).match
                if rule.filterstage in ('both', 'request'):
                    delete[wc.filter.STAGE_REQUEST_HEADER].append(matcher)
                if rule.filterstage in ('both', 'response'):
                    delete[wc.filter.STAGE_RESPONSE_HEADER].append(matcher)
            else:
                # name, value must be ASCII strings
                name = str(rule.name)
                val = str(rule.value)
                if rule.filterstage in ('both', 'request'):
                    add[wc.filter.STAGE_REQUEST_HEADER].append((name, val))
                if rule.filterstage in ('both', 'response'):
                    add[wc.filter.STAGE_RESPONSE_HEADER].append((name, val))
        d['header_add'] = add
        d['header_delete'] = delete
        return d

    def doit (self, data, attrs):
        """
        Apply stored header rules to data, which is a WcMessage object.
        """
        delete = sets.Set()
        # stage is STAGE_REQUEST_HEADER or STAGE_RESPONSE_HEADER
        stage = attrs['filterstage']
        for h in data.keys():
            for name_match in attrs['header_delete'][stage]:
                if name_match(h):
                    wc.log.debug(wc.LOG_FILTER,
                                 "%s removing header %r", self, h)
                    delete.add(h.lower())
                    # go to next header name
                    break
        wc.proxy.Headers.remove_headers(data, delete)
        for name, val in attrs['header_add'][stage]:
            wc.log.debug(wc.LOG_FILTER,
                         "%s adding header %r: %r", self, name, val)
            data[name] = val+"\r"
        return data
