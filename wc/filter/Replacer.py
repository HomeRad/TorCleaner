"""replace expressions in a data stream
you can use this for
- highlighting
- removing/replacing certain strings
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

from wc.filter import FILTER_RESPONSE_MODIFY, compileRegex, compileMime
from wc.filter.Filter import Filter

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['replacer']
mimelist = map(compileMime, ['text/html', 'text/javascript'])


# XXX group matches?
class Replacer (Filter):
    """replace regular expressions in a data stream"""

    def addrule (self, rule):
        super(Replacer, self).addrule(rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")
        compileRegex(rule, "search")

    def filter (self, data, **attrs):
        if not attrs.has_key('buf'): return data
        return attrs['buf'].replace(data)

    def finish (self, data, **attrs):
        if not attrs.has_key('buf'): return data
        buf = attrs['buf']
        if data: data = buf.replace(data)
        return data+buf.flush()

    def getAttrs (self, headers, url):
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return {}
        return {'buf': Buf(rules)}


class Buf (object):
    def __init__ (self, rules):
        self.rules = rules
        self.buf = ""

    def replace (self, data):
        self.buf += data
        if len(self.buf) > 512:
            self._replace()
            if len(self.buf) > 256:
                data = self.buf
                self.buf = self.buf[-256:]
                return data[:-256]
        return ""

    def _replace (self):
        for rule in self.rules:
            if rule.search:
                self.buf = rule.search.sub(rule.replace, self.buf)

    def flush (self):
        self._replace()
        self.buf, data = "", self.buf
        return data
