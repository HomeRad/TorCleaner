# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Basic filter class and routines.
"""

import re
from .. import log, LOG_FILTER


class Filter(object):
    """
    The base filter class.
    """

    def __init__(self, stages=None, rulenames=None, mimes=None):
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
        # cache for mime application {mime (string) -> applies to it (bool)}
        self.mime_cache = {}

    def addrule(self, rule):
        """
        Append given rule to rule list.
        """
        log.debug(LOG_FILTER, "enable %s ", rule)
        for r in self.rules:
            assert r.sid != rule.sid
        self.rules.append(rule)

    def filter(self, data, attrs):
        """
        Filter given data. The data must be non-empty.

        @param attrs: filter-specific state data
        """
        return self.doit(data, attrs)

    def finish(self, data, attrs):
        """
        Filter given data and finish filtering (eg flushing buffers).
        The data may be empty.

        @param attrs: filter-specific state data
        """
        return self.doit(data, attrs)

    def doit(self, data, attrs):
        """
        Filter given data.

        @param attrs: filter-specific state data
        """
        return data

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        Update filter-specific state data for all given filter stages.

        @param attrs: the attributes to update
        @param url: the complete request url
        @param stages: filter stages (STAGE_*)
        @param headers: dictionary with WcMessage objects under the keys
            ``client``, ``server`` and ``data``
        """
        # nothing to to per default
        pass

    def applies_to_stages(self, stages):
        """
        Ask if this filter applies to one of the given filter stages.
        """
        return [s for s in self.stages if s in stages]

    def applies_to_mime(self, mime):
        """
        Ask if this filter applies to a mime type.
        """
        if mime not in self.mime_cache:
            if not self.mimes:
                self.mime_cache[mime] = True
            elif mime is None:
                self.mime_cache[mime] = False
            else:
                self.mime_cache[mime] = \
                       [ro for ro in self.mimes if ro.match(mime)]
        return self.mime_cache[mime]

    def which_rules(self, url, mime):
        """
        Check which rules apply to the given url/mime.  Returns
        a list of tuples (applies, reason, rule)
        """
        applies = []
        # resort rules by dynamic order
        rules = self.rules[:]
        rules.sort(key=lambda x: x.oid)
        for rule in rules:
            if not rule.applies_to_url(url):
                applies.append((False, 'url', rule))
            elif not rule.applies_to_mime(mime):
                applies.append((False, 'mime', rule))
            else:
                applies.append((True, '', rule))
        return applies

    def __cmp__(self, other):
        """
        Compare function considering filter priority.
        """
        return cmp(self.prio, other.prio)

    def __str__(self):
        return self.__class__.__name__
