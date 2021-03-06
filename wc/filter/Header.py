# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Add or delete HTTP headers.
"""

import re
import string
from .. import log, LOG_FILTER, proxy, filter
from . import Filter


class Header(Filter.Filter):
    """
    Filter for adding, modifying and deleting headers.
    """

    enable = True

    def __init__(self):
        """
        Init stages and rulenames.
        """
        stages = [filter.STAGE_REQUEST_HEADER,
                  filter.STAGE_RESPONSE_HEADER]
        rulenames = ['header']
        super(Header, self).__init__(stages=stages, rulenames=rulenames)

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        Configure header rules to add/delete.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(Header, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        delete = {
            filter.STAGE_REQUEST_HEADER: [],
            filter.STAGE_RESPONSE_HEADER: [],
        }
        replace = {
            filter.STAGE_REQUEST_HEADER: [],
            filter.STAGE_RESPONSE_HEADER: [],
        }
        add = {
            filter.STAGE_REQUEST_HEADER: [],
            filter.STAGE_RESPONSE_HEADER: [],
        }
        for rule in self.rules:
            # filter out unwanted rules
            if not rule.applies_to_url(url) or not rule.header:
                continue
            if rule.action == 'remove':
                # No value means header name should be removed.
                # Removal can apply to many header names, so treat name as
                # a regular expression.
                matcher = re.compile(rule.header, re.I).match
                if rule.filterstage in ('both', 'request'):
                    delete[filter.STAGE_REQUEST_HEADER].append(matcher)
                if rule.filterstage in ('both', 'response'):
                    delete[filter.STAGE_RESPONSE_HEADER].append(matcher)
            else:
                # name, value must be ASCII strings
                name = str(rule.header)
                val = str(rule.value)
                if rule.action == "add":
                    d = add
                elif rule.action == "replace":
                    d = replace
                else:
                    raise ValueError("Invalid rule action %r" % rule.action)
                if rule.filterstage in ('both', 'request'):
                    d[filter.STAGE_REQUEST_HEADER].append((name, val))
                if rule.filterstage in ('both', 'response'):
                    d[filter.STAGE_RESPONSE_HEADER].append((name, val))
        attrs['header_add'] = add
        attrs['header_replace'] = replace
        attrs['header_delete'] = delete

    def doit(self, data, attrs):
        """
        Apply stored header rules to data, which is a WcMessage object.
        """
        delete = set()
        # stage is STAGE_REQUEST_HEADER or STAGE_RESPONSE_HEADER
        stage = attrs['filterstage']
        for h in data.keys():
            for name_match in attrs['header_delete'][stage]:
                if name_match(h):
                    log.debug(LOG_FILTER, "%s removing header %r", self, h)
                    delete.add(h.lower())
                    # go to next header name
                    break
        if delete:
            proxy.Headers.remove_headers(data, delete)
        for name, val in attrs['header_add'][stage]:
            if "$" in val:
                # substitute template
                d = {"host": attrs['headers']['client'].get('Host', '')}
                val = string.Template(val).safe_substitute(d)
            log.debug(LOG_FILTER,
                         "%s adding header %r: %r", self, name, val)
            data[name] = val+"\r"
        for name, val in attrs['header_replace'][stage]:
            if name not in data:
                continue
            if "$" in val:
                # substitute template
                d = {"host": attrs['headers']['client'].get('Host', '')}
                val = string.Template(val).safe_substitute(d)
            log.debug(LOG_FILTER,
                         "%s replacing header %r: %r", self, name, val)
            data[name] = val+"\r"
        return data
