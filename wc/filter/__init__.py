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
to see how it is done.

To communicate with the proxy, filters can throw FilterExceptions.
Of course, these must be handled in the appropriate proxy functions
to work properly.

"""
import re

import wc
import wc.log
import wc.configuration
import wc.filter.rules
import wc.proxy.Headers

# filter stages

# Filter complete request (eg. Block filter module)
STAGE_REQUEST = "Request"
# Outgoing header manglers
STAGE_REQUEST_HEADER = "Request header"
# May decode outgoing content.
STAGE_REQUEST_DECODE = "Request decode"
# May modify outgoing content.
STAGE_REQUEST_MODIFY = "Request modify"
# May modify outgoing content.
STAGE_REQUEST_ENCODE = "Request encode"
# Filter complete response
STAGE_RESPONSE = "Response"
# Filter complete response
STAGE_RESPONSE_HEADER = "Response header"
# May decode incoming content
STAGE_RESPONSE_DECODE = "Response decode"
# May modify incoming content
STAGE_RESPONSE_MODIFY = "Response modify"
# May encode incoming content
STAGE_RESPONSE_ENCODE = "Response encode"

FilterStages = [
    STAGE_REQUEST,
    STAGE_REQUEST_HEADER,
    STAGE_REQUEST_DECODE,
    STAGE_REQUEST_MODIFY,
    STAGE_REQUEST_ENCODE,
    STAGE_RESPONSE,
    STAGE_RESPONSE_HEADER,
    STAGE_RESPONSE_DECODE,
    STAGE_RESPONSE_MODIFY,
    STAGE_RESPONSE_ENCODE,
]

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


def compile_mime (mime):
    """compile mimelist entry to regex object and return it"""
    return re.compile("^(?i)%s(;.+)?$"%mime)


def GetRuleFromName (name):
    """return new rule instance for given rule name"""
    name = '%sRule' % name.capitalize()
    mod = __import__("wc.filter.rules.%s"%name, {}, {}, [name])
    return getattr(mod, name)()


def applyfilter (data, fun, attrs):
    """Apply all filters which are registered in the given filter stage.
       For different filter stages we have different data objects.
       Look at the filter examples.
    """
    filterstage = attrs['filterstage']
    wc.log.debug(wc.LOG_FILTER, "Filter (%s) %d bytes in %s..",
                 fun, len(data), filterstage)
    if attrs.get('nofilter') or (fun!='finish' and not data):
        wc.log.debug(wc.LOG_FILTER, "..don't filter")
        return data
    filters = wc.configuration.config['filterlist'][filterstage]
    for f in filters:
        wc.log.debug(wc.LOG_FILTER, "..filter with %s" % f)
        ffun = getattr(f, fun)
        if f.applies_to_mime(attrs['mime']):
            wc.log.debug(wc.LOG_FILTER, "..applying")
            data = ffun(data, attrs)
        else:
            wc.log.debug(wc.LOG_FILTER, "..not applying")
    wc.log.debug(wc.LOG_FILTER, "..result %d bytes", len(data))
    return data


def get_filterattrs (url, filterstage, browser='Calzilla/6.0',
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
        'mime_types': None,
        'headers': attrheaders,
        'browser': browser,
        'filterstage': filterstage,
    }
    if attrs['mime']:
        charset = get_mime_charset(attrs['mime'])
        if charset:
            attrs['charset'] = charset
    for f in wc.configuration.config['filterlist'][filterstage]:
        # note: get attributes of _all_ filters since the
        # mime type can change dynamically
        attrs.update(f.get_attrs(url, filterstage, attrheaders))
    return attrs


def get_mime_charset (mime):
    """extract charset information from mime string
       eg. text/html; charset=iso8859-1
    """
    for param in mime.split(';'):
        if param.lower().startswith('charset='):
            return param[8:]
    return None
