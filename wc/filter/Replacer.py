# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
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
Replace expressions in a data stream. Use this for highlighting and
removing/replacing certain strings.
"""

from . import Filter, STAGE_RESPONSE_MODIFY
from .. import fileutil

DefaultCharset = 'iso-8859-1'

class Replacer (Filter.Filter):
    """Replace regular expressions in a data stream."""

    enable = True

    def __init__ (self):
        """Initialize replacer flags."""
        stages = [STAGE_RESPONSE_MODIFY]
        rulenames = ['replace']
        mimes = ['text/html', 'text/xml', 'application/xml',
                 r'application/(atom|rss|rdf)\+xml',
                 'text/javascript', 'application/x-javascript',]
        super(Replacer, self).__init__(stages=stages, mimes=mimes,
                                       rulenames=rulenames)

    def filter (self, data, attrs):
        """Feed data to replacer buffer."""
        if 'replacer_buf' not in attrs:
            return data
        buf = attrs['replacer_buf']
        buf.mime = attrs['mime']
        charset = attrs.get('charset', DefaultCharset)
        return self.replace(data, charset, buf.filter)

    def finish (self, data, attrs):
        """Feed data to replacer buffer, flush and return it."""
        if 'replacer_buf' not in attrs:
            return data
        buf = attrs['replacer_buf']
        buf.mime = attrs['mime']
        charset = attrs.get('charset', DefaultCharset)
        return self.replace(data, charset, buf.finish)

    def replace (self, data, charset, func):
        """Decode data, replace contents of buffer and encode again."""
        udata = data.decode(charset, 'ignore')
        udata = func(udata)
        return udata.encode(charset, 'ignore')

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """Initialize replacer buffer object."""
        if not self.applies_to_stages(stages):
            return
        parent = super(Replacer, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        if not rules:
            return
        attrs['replacer_buf'] = Buf(rules)


# 4kB chunk, 1024 Byte overlap
CHUNK_SIZE = 1024L*4L
CHUNK_OVERLAP = 1024L

class Buf (fileutil.Buffer):
    """
    Holds buffer data ready for replacing, with overlapping scans.
    Strings must be unicode.
    """

    def __init__ (self, rules):
        """Store rules and initialize buffer."""
        super(Buf, self).__init__(empty=u"")
        self.rules = rules
        self.mime = None

    def filter (self, data):
        """Fill up buffer with given data, and scan for replacements."""
        self.write(data)
        if len(self) > CHUNK_SIZE:
            return self._replace(self.flush(overlap=CHUNK_OVERLAP))
        return u""

    def finish (self, data):
        self.write(data)
        return self._replace(self.flush())

    def _replace (self, data):
        """Scan for replacements."""
        for rule in self.rules:
            if rule.search and rule.applies_to_mime(self.mime):
                data = rule.search_ro.sub(rule.replacement, data)
        return data
