"""replace expressions in a data stream
you can use this for
- highlighting
- removing/replacing certain strings
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
import re
from Rules import STARTTAG, ENDTAG, DATA, COMMENT
from wc.filter import FILTER_RESPONSE_MODIFY, Filter, compileRegex, compileMime

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
        Filter.addrule(self, rule)
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
        # weed out the rules that dont apply to this url
        rules = filter(lambda r, u=url: r.appliesTo(u), self.rules)
        if not rules:
            return {}
        return {'buf': Buf(rules)}


# buffer size in bytes
BUF_SIZE=512

class Buf:
    def __init__ (self, rules):
        self.buf = ""
        self.rules = rules

    def replace (self, data):
        data = self.buf + data
        for rule in self.rules:
            data = rule.search.sub(rule.replace, data)
        self.buf = data[-BUF_SIZE:]
        return data[:-BUF_SIZE]

    def flush (self):
        return self.buf
