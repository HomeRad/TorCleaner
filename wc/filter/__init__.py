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
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

import re, wc, wc.filter.rules
from wc.proxy.Headers import WcMessage
from cStringIO import StringIO

# filter order
FILTER_REQUEST         = 0 # Filter complete request (blocking)
FILTER_REQUEST_HEADER  = 1 # Outgoing header manglers
FILTER_REQUEST_DECODE  = 2 # May decode outgoing content.
FILTER_REQUEST_MODIFY  = 3 # May modify outgoing content.
FILTER_REQUEST_ENCODE  = 4 # May encode outgoing content.
FILTER_RESPONSE        = 5 # Filter complete response
FILTER_RESPONSE_HEADER = 6 # Incoming header manglers
FILTER_RESPONSE_DECODE = 7 # May decode incoming content
FILTER_RESPONSE_MODIFY = 8 # May modify incoming content
FILTER_RESPONSE_ENCODE = 9 # May encode incoming content

class FilterException (Exception):
    """Generic filter exception"""
    pass


class FilterWait (FilterException):
    """Raised when filter wait for more data to filter. The filter
       has to buffer already passed data until the next call.
    """
    pass


def printFilterOrder (i):
    if i==FILTER_REQUEST:
        s = "Request"
    elif i==FILTER_REQUEST_HEADER:
        s = "Request Header"
    elif i==FILTER_REQUEST_DECODE:
        s = "Request Decode"
    elif i==FILTER_REQUEST_MODIFY:
        s = "Request Modify"
    elif i==FILTER_REQUEST_ENCODE:
        s = "Request Encode"
    elif i==FILTER_RESPONSE:
        s = "Response"
    elif i==FILTER_RESPONSE_HEADER:
        s = "Response Header"
    elif i==FILTER_RESPONSE_DECODE:
        s = "Response Decode"
    elif i==FILTER_RESPONSE_MODIFY:
        s = "Response Modify"
    elif i==FILTER_RESPONSE_ENCODE:
        s = "Response Encode"
    else:
        s = "Invalid"
    return s


# compile object attribute
def compileRegex (obj, attr):
    if hasattr(obj, attr) and getattr(obj, attr):
        setattr(obj, attr+"_ro", re.compile(getattr(obj, attr)))


# compile mimelist entry
def compileMime (mime):
    return re.compile("^(?i)%s(;.+)?$"%mime)


def GetRuleFromName (name):
    name = '%sRule' % name.capitalize()
    return getattr(wc.filter.rules, name)()


def applyfilter (i, data, fun, attrs):
    """Apply all filters which are registered in filter level i.
    For different filter levels we have different data objects.
    Look at the filter examples.
    """
    if attrs.get('nofilter') or (fun!='finish' and not data):
        return data
    for f in wc.config['filterlist'][i]:
        ffun = getattr(f, fun)
        if attrs.has_key('mime'):
            if f.applies_to_mime(attrs['mime']):
                data = ffun(data, **attrs)
        else:
            data = ffun(data, **attrs)
    return data


default_headers = WcMessage(StringIO('Content-Type: text/html\r\n\r\n'))
def get_filterattrs (url, filters, headers=default_headers):
    """init external state objects"""
    attrs = {
        'url': url,
        'nofilter': wc.config.nofilter(url),
        'mime' : headers.get('Content-Type', 'application/octet-stream'),
        'headers': headers,
    }
    for i in filters:
        for f in wc.config['filterlist'][i]:
            if f.applies_to_mime(attrs['mime']):
                attrs.update(f.getAttrs(url, headers))
    return attrs
