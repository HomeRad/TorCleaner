# -*- coding: iso-8859-1 -*-
"""replace expressions in a data stream
   you can use this for highlighting and removing/replacing certain strings
"""
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

import wc.filter
import wc.filter.Filter


DefaultCharset = 'iso-8859-1'

# XXX group matches?
class Replacer (wc.filter.Filter.Filter):
    """replace regular expressions in a data stream"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['replace']
    mimelist = [wc.filter.compile_mime(x)
       for x in ['text/html', 'text/javascript', 'application/x-javascript']]

    def filter (self, data, **attrs):
        """feed data to replacer buffer"""
        if not attrs.has_key('replacer_buf') or not data:
            return data
        buf = attrs['replacer_buf']
        charset = attrs.get('charset', DefaultCharset)
        return self.replace(data, charset, buf)

    def finish (self, data, **attrs):
        """feed data to replacer buffer, flush and return it"""
        if not attrs.has_key('replacer_buf'):
            return data
        buf = attrs['replacer_buf']
        charset = attrs.get('charset', DefaultCharset)
        if data:
            data = self.replace(data, charset, buf)
        return data+buf.flush().encode(charset, 'ignore')

    def replace (self, data, charset, buf):
        udata = data.decode(charset, 'ignore')
        udata = buf.replace(udata)
        return udata.encode(charset, 'ignore')

    def get_attrs (self, url, headers):
        """initialize replacer buffer object"""
        d = super(Replacer, self).get_attrs(url, headers)
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return d
        d['replacer_buf'] = Buf(rules)
        return d


class Buf (object):
    """Holds buffer data ready for replacing, with overlapping scans.
       Strings must be unicode."""

    def __init__ (self, rules):
        """store rules and initialize buffer"""
        self.rules = rules
        self.buf = u""

    def replace (self, data):
        """fill up buffer with given data, and scan for replacements"""
        self.buf += data
        if len(self.buf) > 512:
            self._replace()
            if len(self.buf) > 256:
                data = self.buf
                self.buf = self.buf[-256:]
                return data[:-256]
        return u""

    def _replace (self):
        """scan for replacements"""
        for rule in self.rules:
            if rule.search:
                self.buf = rule.search_ro.sub(rule.replacement, self.buf)

    def flush (self):
        """flush buffered data and return it"""
        self._replace()
        self.buf, data = u"", self.buf
        return data
