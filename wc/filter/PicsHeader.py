"""Parse and filter PICS data.
See http://www.w3.org/PICS/labels.html for more info.
"""
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

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_HEADER,]

# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['pics']

mimelist = []

from wc.filter.Filter import Filter
from wc.filter.PICS import check_pics
from wc.filter import FilterPics


class PicsHeader (Filter):
    def doit (self, data, **attrs):
        rules = attrs['rules']
        headers = attrs['headers']
        if headers.has_key('PICS-Label'):
            for rule in self.rules:
                msg = check_pics(rule, headers['PICS-Label'])
                if msg:
                    raise FilterPics(msg)
        return data


    def getAttrs (self, headers, url):
        # weed out the rules that dont apply to this url
        rules = filter(lambda r, u=url: r.appliesTo(u), self.rules)
        return {'rules': rules,
                'headers': headers}
