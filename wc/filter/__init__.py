"""filter modules

Welcome to the wonderful world of software OSI layer 5 filtering.
If you want to write your own filter module look at the existing
filters.
You can add extern states for the filter by making a separate class
and passing it with the "attrs" parameter. Look at the Rewriter filter
to see how its done.
"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
from wc import debug, _
from wc.debug_levels import *

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
    return re.compile("^%s$"%mime, re.I)

def GetRuleFromName (name):
    name = name.capitalize()+'Rule'
    if hasattr(Rules, name):
        klass = getattr(Rules, name)
        return klass()
    raise ValueError, _("unknown rule name %s")+name


def applyfilter (i, arg, fun='filter', attrs={}):
    """Apply all filters which are registered in filter level i.
    For different filter levels we have different arg objects.
    Look at the filter examples.
    """
    if attrs.get('nofilter'):
        return arg
    try:
        #debug(BRING_IT_ON, 'filter stage', printFilterOrder(i), "(%s)"%fun)
        for f in wc.config['filterlist'][i]:
            ffun = getattr(f, fun)
            if attrs.has_key('mime'):
                if f.applies_to_mime(attrs['mime']):
                    arg = apply(ffun, (arg,), attrs)
            else:
                arg = apply(ffun, (arg,), attrs)
    except FilterException, msg:
        #debug(NIGHTMARE, msg)
        pass
    return arg


def initStateObjects (headers={'content-type': 'text/html'}, url=None):
    """init external state objects"""
    attrs = {'mime': headers.get('content-type', 'application/octet-stream')}
    for i in range(10):
        for f in wc.config['filterlist'][i]:
            if f.applies_to_mime(attrs['mime']):
                attrs.update(f.getAttrs(headers, url))
    return attrs


# The base filter class
class Filter:
    def __init__ (self, mimelist):
        self.rules = []
        self.mimelist = mimelist

    def addrule (self, rule):
        #debug(BRING_IT_ON, "enable %s rule '%s'"%(rule.get_name(),rule.title))
        self.rules.append(rule)

    def filter (self, data, **args):
        return apply(self.doit, (data,), args)

    def finish (self, data, **args):
        return apply(self.doit, (data,), args)

    def doit (self, data, **args):
        return data

    def getAttrs (self, headers, url):
        return {'url': url, 'headers': headers}

    def applies_to_mime (self, mime):
        #debug(HURT_ME_PLENTY, self.__class__.__name__, "applies_to_mime", mime)
        if not self.mimelist:
            #debug(HURT_ME_PLENTY, "no mimelist")
            return 1
        for ro in self.mimelist:
            if ro.match(mime):
                #debug(HURT_ME_PLENTY, "match!")
                return 1
