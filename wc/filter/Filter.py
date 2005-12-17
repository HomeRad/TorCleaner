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
Basic filter class and routines.
"""

import re
import wc
import wc.log


class Filter (object):
    """
    The base filter class.
    """

    def __init__ (self, stages=None, rulenames=None, mimes=None):
        """
        Initialize rule list, mime list, stages, rulenames and priority.
        """
        # Which filter stages this filter applies to.
        # See wc/filter/__init__.py for the list of valid filter stages
        self.stages = []
        if stages is not None:
            self.stages.extend(stages)
        # priority to have over other filters in the same filter stage
        self.prio = -1
        # Which rule types this filter applies to (see Rules.py).
        # All rules of these types get added with Filter.addrule().
        self.rulenames = []
        if rulenames is not None:
            self.rulenames.extend(rulenames)
        # Which mime types this filter applies to.
        if mimes is not None:
            # compile mime list entries to regex objects
            self.mimes = [re.compile(r"^(?i)%s(;.+)?$" % x) for x in mimes]
        else:
            self.mimes = []
        # list of rules this filter is interested in
        self.rules = []

    def addrule (self, rule):
        """
        Append given rule to rule list.
        """
        assert wc.log.debug(wc.LOG_FILTER, "enable %s ", rule)
        for r in self.rules:
            assert r.sid != rule.sid
        self.rules.append(rule)

    def filter (self, data, attrs):
        """
        Filter given data.

        @param attrs: filter-specific state data
        """
        return self.doit(data, attrs)

    def finish (self, data, attrs):
        """
        Filter given data and finish filtering (eg flushing buffers).

        @param attrs: filter-specific state data
        """
        return self.doit(data, attrs)

    def doit (self, data, attrs):
        """
        Filter given data.

        @param attrs: filter-specific state data
        """
        return data

    def get_attrs (self, url, localhost, stages, headers):
        """
        Get filter-specific state data for all given filter stages.

        @param url: the complete request url
        @param stages: filter stages (STAGE_*)
        @param headers: dictionary with WcMessage objects under the keys
            ``client``, ``server`` and ``data``
        """
        return {}

    def applies_to_stages (self, stages):
        """
        Ask if this filter applies to one of the given filter stages.
        """
        return [s for s in self.stages if s in stages]

    def applies_to_mime (self, mime):
        """
        Ask if this filter applies to a mime type.
        """
        if not self.mimes:
            return True
        if mime is None:
            return False
        for ro in self.mimes:
            if ro.match(mime):
                return True
        return False

    def __cmp__ (self, other):
        """
        Compare function considering filter priority.
        """
        return cmp(self.prio, other.prio)

    def __str__ (self):
        return self.__class__.__name__
