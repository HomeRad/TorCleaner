"""Parse and filter PICS data.
See http://www.w3.org/PICS/labels.html for more info.
"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003  Bastian Kleineidam
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

from wc.filter.Filter import Filter
from wc.filter.PICS import pics_add, pics_is_cached
from wc.filter import FILTER_RESPONSE_HEADER

class PicsHeader (Filter):
    """Adds PICS data supplied in header values of 'PICS-Label'"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_HEADER,]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['pics']
    mimelist = []

    def doit (self, data, **attrs):
        url = attrs['url']
        if pics_is_cached(url):
            # we already have PICS data for this url, ignore any new ones
            # note: do not yet check at this point, but give the HTML
            # page a chance to override this with a its own PICS label.
            return data
        rules = attrs['pics_rules']
        headers = attrs['headers']
        if headers.has_key('PICS-Label'):
            pics_add(url, headers['PICS-Label'])
        return data


    def getAttrs (self, url, headers):
        d = super(PicsHeader, self).getAttrs(url, headers)
        # weed out the rules that don't apply to this url
        d['pics_rules'] = [ rule for rule in self.rules if rule.appliesTo(url) ]
        return d
