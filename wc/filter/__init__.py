# -*- coding: iso-8859-1 -*-
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
"""filter modules

Welcome to the wonderful world of software OSI layer 5 filtering.
If you want to write your own filter module look at the existing
filters.

You can add extern states for the filter by making a separate class
and passing it with the "attrs" parameter. Look at the Rewriter filter
to see how its done.

To communicate with the proxy, filters can throw FilterExceptions.
Of course, these must be handled in the appropriate proxy functions
to work properly.

"""
import re

import wc
import wc.configuration
import wc.filter.rules
import wc.proxy.Headers

# filter orders


# Filter complete request (blocking)
FILTER_REQUEST = 0
# Outgoing header manglers
FILTER_REQUEST_HEADER = 1
# May decode outgoing content.
FILTER_REQUEST_DECODE = 2
# May modify outgoing content.
FILTER_REQUEST_MODIFY = 3
# May modify outgoing content.
FILTER_REQUEST_ENCODE = 4
# Filter complete response
FILTER_RESPONSE = 5
# Filter complete response
FILTER_RESPONSE_HEADER = 6
# May decode incoming content
FILTER_RESPONSE_DECODE = 7
# May modify incoming content
FILTER_RESPONSE_MODIFY = 8
# May encode incoming content
FILTER_RESPONSE_ENCODE = 9

FilterOrder = {
    FILTER_REQUEST: "Request",
    FILTER_REQUEST_HEADER: "Request Header",
    FILTER_REQUEST_DECODE: "Request Decode",
    FILTER_REQUEST_MODIFY: "Request Modify",
    FILTER_REQUEST_ENCODE: "Request Encode",
    FILTER_RESPONSE: "Response",
    FILTER_RESPONSE_HEADER: "Response Header",
    FILTER_RESPONSE_DECODE: "Response Decode",
    FILTER_RESPONSE_MODIFY: "Response Modify",
    FILTER_RESPONSE_ENCODE: "Response Encode",
}

class FilterException (Exception):
    """Generic filter exception"""
    pass


class FilterWait (FilterException):
    """Raised when a filter waits for more data. The filter should
       buffer the already passed data until the next call (and until
       it has enough data to proceed).
    """
    pass


class FilterRating (FilterException):
    """Raised when a filter detected rated content.
       The proxy must not have sent any content.
    """
    pass


class FilterProxyError (FilterException):
    """Raised to signal a proxy error which should be delegated to
       the HTTP client."""
    def __init__ (self, status, msg, text):
        self.status = status
        self.msg = msg
        self.text = text


def printFilterOrder (i):
    """return string representation of filter order i"""
    return FilterOrder.get(i, "Invalid")


def compile_mime (mime):
    """compile mimelist entry to regex object and return it"""
    return re.compile("^(?i)%s(;.+)?$"%mime)


def GetRuleFromName (name):
    """return new rule instance for given rule name"""
    name = '%sRule' % name.capitalize()
    mod = __import__("wc.filter.rules.%s"%name, {}, {}, [name])
    return getattr(mod, name)()


def applyfilter (i, data, fun, attrs):
    """Apply all filters which are registered in filter level i.
    For different filter levels we have different data objects.
    Look at the filter examples.
    """
    if attrs.get('nofilter') or (fun!='finish' and not data):
        return data
    return _applyfilter(i, data, fun, attrs)


def _applyfilter (i, data, fun, attrs):
    attrs['filterstage'] = i
    for f in wc.configuration.config['filterlist'][i]:
        ffun = getattr(f, fun)
        if f.applies_to_mime(attrs['mime']):
            wc.log.debug(wc.LOG_FILTER, "filter %d bytes with %s",
                         len(data), f)
            data = ffun(data, **attrs)
    return data


def applyfilters (levels, data, fun, attrs):
    """Apply all filters which are registered in filter levels.
    For different filter levels we have different data objects.
    Look at the filter examples.
    """
    if attrs.get('nofilter') or (fun!='finish' and not data):
        return data
    for i in levels:
        data = _applyfilter(i, data, fun, attrs)
    return data


def get_filterattrs (url, filterstages, browser='Calzilla/6.0',
                     clientheaders=None, serverheaders=None, headers=None):
    """init external state objects"""
    if clientheaders is None:
        clientheaders = wc.proxy.Headers.WcMessage()
    if serverheaders is None:
        serverheaders = wc.proxy.Headers.WcMessage()
    if headers is None:
        headers = wc.proxy.Headers.WcMessage()
    attrheaders = {
        'client': clientheaders,
        'server': serverheaders,
        'data': headers,
    }
    attrs = {
        'url': url,
        'nofilter': wc.configuration.config.nofilter(url),
        'mime' : headers.get('Content-Type'),
        'headers': attrheaders,
        'browser': browser,
    }
    if attrs['mime']:
        charset = get_mime_charset(attrs['mime'])
        if charset:
            attrs['charset'] = charset
    for i in filterstages:
        for f in wc.configuration.config['filterlist'][i]:
            # note: get attributes of _all_ filters since the
            # mime type can change dynamically
            attrs.update(f.get_attrs(url, attrheaders))
    return attrs


def get_mime_charset (mime):
    """extract charset information from mime string
       eg. text/html; charset=iso8859-1
    """
    for param in mime.split(';'):
        if param.lower().startswith('charset='):
            return param[8:]
    return None
