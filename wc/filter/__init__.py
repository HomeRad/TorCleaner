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
Filter modules.

Welcome to the wonderful world of software OSI layer 5 filtering.
To be able to filter every aspect of the HTTP protocol data, different
data stages are defined. Each of these can be separately filtered.

- HTTP request line
- HTTP request headers
- HTTP request content body
- HTTP response line
- HTTP response headers
- HTTP response content body

Since content bodies can be encoded (specified by the Content-Encoding
header) they both have methods for decoding, filtering and re-encoding
the body data.

The content body is usual HTML data for the browser, but could also be
something else. The type of data is specified by the Content-Type
header and resembles a MIME type.
Each filter for content bodies can apply to specific MIME type. For
example the XmlRewriter filter applies only to XML data.

You can add extern states for the filter by making a separate class
and passing it with the "attrs" parameter. Look at the HtmlRewriter
filter to see how it is done.

To communicate with the proxy, filters can throw FilterExceptions.
These must be handled in the appropriate proxy functions to work
properly.
"""

import wc
import wc.log
import wc.configuration
import wc.filter.rules
import wc.http.header
import wc.HtmlParser

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
    """
    Generic filter exception.
    """
    pass


class FilterWait (FilterException):
    """
    Raised when a filter waits for more data. The filter should
    buffer the already passed data until the next call (and until
    it has enough data to proceed).
    """
    pass


class FilterRating (FilterException):
    """
    Raised when a filter detected rated content.
    The proxy must not have sent any content.
    """
    pass


class FilterProxyError (FilterException):
    """
    Raised to signal a proxy error which should be delegated to
    the HTTP client.
    """
    def __init__ (self, status, msg, text):
        self.status = status
        self.msg = msg
        self.text = text


def GetRuleFromName (name):
    """
    Return new rule instance for given rule name.
    """
    name = '%sRule' % name.capitalize()
    mod = __import__("wc.filter.rules.%s"%name, {}, {}, [name])
    return getattr(mod, name)()


def applyfilter (filterstage, data, fun, attrs):
    """
    Apply all filters which are registered in the given filter stage.
    For different filter stages we have different data objects.
    Look at the filter examples.
    """
    attrs['filterstage'] = filterstage
    assert wc.log.debug(wc.LOG_FILTER, "Filter (%s) %d bytes in %s..",
                        fun, len(data), filterstage)
    if attrs.get('nofilter') or (fun != 'finish' and not data):
        assert wc.log.debug(wc.LOG_FILTER, "..don't filter")
        return data
    for f in wc.configuration.config['filterlist'][filterstage]:
        assert wc.log.debug(wc.LOG_FILTER, "..filter with %s" % f)
        if f.applies_to_mime(attrs['mime']):
            assert wc.log.debug(wc.LOG_FILTER, "..applying")
            data = getattr(f, fun)(data, attrs)
        else:
            assert wc.log.debug(wc.LOG_FILTER, "..not applying")
    assert wc.log.debug(wc.LOG_FILTER, "..result %d bytes", len(data))
    return data


def get_filterattrs (url, localhost, filterstages, browser='Calzilla/6.0',
                     clientheaders=None, serverheaders=None, headers=None):
    """
    Init external state objects.
    """
    if clientheaders is None:
        clientheaders = wc.http.header.WcMessage()
    if serverheaders is None:
        serverheaders = wc.http.header.WcMessage()
    if headers is None:
        headers = wc.http.header.WcMessage()
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
    }
    if attrs['mime']:
        charset = wc.HtmlParser.get_ctype_charset(attrs['mime'])
        if charset is not None:
            attrs['charset'] = charset
    for f in wc.configuration.config['filtermodules']:
        # note: get attributes of _all_ filters since the
        # mime type can change dynamically
        attrs.update(f.get_attrs(url, localhost, filterstages, attrheaders))
    return attrs
