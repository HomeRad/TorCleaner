# -*- coding: iso-8859-1 -*-
"""basic filter class and routines"""
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

import wc
import wc.log


class Filter (object):
    """the base filter class"""

    mimelist = []

    def __init__ (self):
        """initialize rule list and priority"""
        self.rules = []
        self.prio = -1

    def addrule (self, rule):
        """append given rule to rule list"""
        wc.log.debug(wc.LOG_FILTER, "enable %s ", rule)
        self.rules.append(rule)

    def filter (self, data, attrs):
        """Filter given data.

           @param attrs filter-specific state data
        """
        return self.doit(data, attrs)

    def finish (self, data, attrs):
        """Filter given data and finish filtering (eg flushing buffers).

           @param attrs filter-specific state data
        """
        return self.doit(data, attrs)

    def doit (self, data, attrs):
        """Filter given data.

           @param attrs filter-specific state data
        """
        return data

    def get_attrs (self, url, headers):
        """get filter-specific state data

           @param url the complete request url
           @param headers dictionary with WcMessage objects under the keys
                  ``client``, ``server`` and ``data``
        """
        return {}

    def applies_to_mime (self, mime):
        """ask if this filter applies to a mime type"""
        if not self.mimelist:
            return True
        if mime is None:
            return False
        for ro in self.mimelist:
            if ro.match(mime):
                return True
        return False

    def __cmp__ (self, other):
        """compare function considering filter priority"""
        return cmp(self.prio, other.prio)
