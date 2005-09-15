# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Recognize MIME types.
"""

import cStringIO as StringIO
import mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'

import wc.log
import wc.filter
import wc.filter.Filter
import wc.magic


class MimeRecognizer (wc.filter.Filter.Filter):
    """
    Recognizes missing or wrong content type header of URLs request data.
    """

    enable = True

    def __init__ (self):
        """
        Initialize image reducer flags.
        """
        stages = [wc.filter.STAGE_RESPONSE_DECODE]
        super(MimeRecognizer, self).__init__(stages=stages)
        # minimal number of bytes to start mime recognition
        self.minimal_size_bytes = 5
        # sufficient number of bytes to start mime recognition
        self.sufficient_size_bytes = 1024

    def filter (self, data, attrs):
        """
        Feed data to recognizer.
        """
        if not attrs.has_key('mimerecognizer_buf') or \
           attrs.get('mimerecognizer_ignore'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        if buf.tell() >= self.sufficient_size_bytes:
            return self.recognize(buf, attrs)
        return ''

    def finish (self, data, attrs):
        """
        Feed data to recognizer.
        """
        if not attrs.has_key('mimerecognizer_buf') or \
           attrs.get('mimerecognizer_ignore'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        if buf.tell() >= self.minimal_size_bytes:
            return self.recognize(buf, attrs)
        data = buf.getvalue()
        buf.close()
        return data

    def recognize (self, buf, attrs):
        """
        Try to recognize MIME type and write Content-Type header.
        """
        # note: recognizing a mime type fixes exploits like
        # CVE-2002-0025 and CVE-2002-0024
        wc.log.debug(wc.LOG_FILTER, "MIME recognize %d bytes of data",
                     buf.tell())
        try:
            mime = wc.magic.classify(buf)
            wc.log.debug(wc.LOG_FILTER, "MIME recognized %r", mime)
            origmime = attrs['mime']
            if mime is not None and origmime is not None and \
               not origmime.startswith(mime):
                wc.log.warn(wc.LOG_FILTER, "Adjusting MIME %r -> %r at %r",
                            origmime, mime, attrs['url'])
                attrs['mime'] = mime
                attrs['headers']['data']['Content-Type'] = "%s\r" % mime
        except StandardError:
            wc.log.warn(wc.LOG_FILTER,
                        "Mime recognize error at %r (%r)",
                        attrs['url'], buf.getvalue())
        data = buf.getvalue()
        buf.close()
        return data

    def get_attrs (self, url, localhost, stages, headers):
        """
        Initialize buffer.
        """
        if not self.applies_to_stages(stages):
            return {}
        d = super(MimeRecognizer, self).get_attrs(url, localhost, stages, headers)
        d['mimerecognizer_buf'] = StringIO.StringIO()
        d['mimerecognizer_ignore'] = False
        return d
