"""filter modules

Welcome to the wonderful world of software OSI layer 5 filtering.
If you want to write your own filter module look at the existing
filters.
You can add extern states for the filter by making a separate class
and passing it with the "attrs" parameter. Look at the Rewriter filter
to see how its done.
"""
# Copyright (C) 2000-2002  Bastian Kleineidam
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

import sys, re, wc
from wc.debug import *

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

class FilterException (Exception): pass


def printFilterOrder (i):
    if   i==FILTER_REQUEST: return "Request"
    elif i==FILTER_REQUEST_HEADER: return "Request Header"
    elif i==FILTER_REQUEST_DECODE: return "Request Decode"
    elif i==FILTER_REQUEST_MODIFY: return "Request Modify"
    elif i==FILTER_REQUEST_ENCODE: return "Request Encode"
    elif i==FILTER_RESPONSE: return "Response"
    elif i==FILTER_RESPONSE_HEADER: return "Response Header"
    elif i==FILTER_RESPONSE_DECODE: return "Response Decode"
    elif i==FILTER_RESPONSE_MODIFY: return "Response Modify"
    elif i==FILTER_RESPONSE_ENCODE: return "Response Encode"
    return "Invalid"


# compile object attribute
def compileRegex (obj, attr):
    if hasattr(obj, attr) and getattr(obj, attr):
        setattr(obj, attr, re.compile(getattr(obj, attr)))

# compile mimelist entry
def compileMime (mime):
    return re.compile("^(?i)%s(;.+)?$"%mime)


def GetRuleFromName (name):
    name = name.capitalize()+'Rule'
    exec "from wc.filter.rules.%s import %s"%(name,name)
    klass = locals()[name]
    return klass()


def applyfilter (i, data, fun='filter', attrs={}):
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
                data = apply(ffun, (data,), attrs)
        else:
            data = apply(ffun, (data,), attrs)
    return data


def initStateObjects (headers={'Content-Type': 'text/html'}, url=None):
    """init external state objects"""
    attrs = {'mime': headers.get('Content-Type', 'application/octet-stream')}
    for i in range(10):
        for f in wc.config['filterlist'][i]:
            if f.applies_to_mime(attrs['mime']):
                attrs.update(f.getAttrs(headers, url))
    return attrs

