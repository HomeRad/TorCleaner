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
Replace expressions in a data stream. Use this for highlighting and
removing/replacing certain strings.
"""

import wc.filter
import wc.filter.Filter


DefaultCharset = 'iso-8859-1'

class Replacer (wc.filter.Filter.Filter):
    """
    Replace regular expressions in a data stream.
    """

    enable = True

    def __init__ (self):
        """
        Initialize replacer flags.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ['replace']
        mimes = ['text/html',
                 'text/xml', 'application/xml', 'application/atom+xml',
                 'text/javascript', 'application/x-javascript',]
        super(Replacer, self).__init__(stages=stages, mimes=mimes,
                                       rulenames=rulenames)

    def filter (self, data, attrs):
        """
        Feed data to replacer buffer.
        """
        if not attrs.has_key('replacer_buf'):
            return data
        buf = attrs['replacer_buf']
        buf.mime = attrs['mime']
        charset = attrs.get('charset', DefaultCharset)
        return self.replace(data, charset, buf)

    def finish (self, data, attrs):
        """
        Feed data to replacer buffer, flush and return it.
        """
        if not attrs.has_key('replacer_buf'):
            return data
        buf = attrs['replacer_buf']
        buf.mime = attrs['mime']
        charset = attrs.get('charset', DefaultCharset)
        if data:
            data = self.replace(data, charset, buf)
        return data+buf.flush().encode(charset, 'ignore')

    def replace (self, data, charset, buf):
        """
        Decode data, replace contents of buffer and encode again.
        """
        udata = data.decode(charset, 'ignore')
        udata = buf.replace(udata)
        return udata.encode(charset, 'ignore')

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        Initialize replacer buffer object.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(Replacer, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        if not rules:
            return
        attrs['replacer_buf'] = Buf(rules)


class Buf (object):
    """
    Holds buffer data ready for replacing, with overlapping scans.
    Strings must be unicode.
    """

    def __init__ (self, rules):
        """
        Store rules and initialize buffer.
        """
        self.rules = rules
        self.buf = u""
        self.mime = None

    def replace (self, data):
        """
        Fill up buffer with given data, and scan for replacements.
        """
        self.buf += data
        if len(self.buf) > 512:
            self._replace()
            if len(self.buf) > 256:
                data = self.buf
                self.buf = self.buf[-256:]
                return data[:-256]
        return u""

    def _replace (self):
        """
        Scan for replacements.
        """
        for rule in self.rules:
            if rule.search and rule.applies_to_mime(self.mime):
                self.buf = rule.search_ro.sub(rule.replacement, self.buf)

    def flush (self):
        """
        Flush buffered data and return it.
        """
        self._replace()
        self.buf, data = u"", self.buf
        return data
