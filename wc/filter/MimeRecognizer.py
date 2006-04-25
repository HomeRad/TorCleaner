# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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


def is_preferred_mime (mime, origmime):
    """
    See if the newly found mime is preferred over the original one.
    @param mime: MIME type from magic module.
    @type mime: string
    @param origmime: original MIME type
    @type origmime: string
    """
    if mime == origmime:
        return False
    # New mime could be same as orig, but without appendix. Example:
    # mime="text/html", origmime="text/html; charset=UTF8"
    if origmime.startswith(mime+";"):
        return False
    # Sometimes text/html is recognized as text/plain.
    if origmime.startswith("text/html") and mime.startswith("text/"):
        return False
    return True


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
        if 'mimerecognizer_buf' not in attrs or \
           'mimerecognizer_ignore' in attrs:
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
        if 'mimerecognizer_buf' not in attrs or \
           'mimerecognizer_ignore' in attrs:
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
        """Try to recognize MIME type and write Content-Type header."""
        # note: recognizing a mime type fixes exploits like
        # CVE-2002-0025 and CVE-2002-0024
        assert wc.log.debug(wc.LOG_FILTER, "MIME recognize %d bytes of data",
                     buf.tell())
        try:
            mime = wc.magic.classify(buf)
            assert wc.log.debug(wc.LOG_FILTER, "MIME recognized %r", mime)
            origmime = attrs['mime']
            if mime and origmime and is_preferred_mime(mime, origmime):
                wc.log.info(wc.LOG_FILTER, "Adjusting MIME %r -> %r at %r",
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

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """Initialize buffer."""
        if not self.applies_to_stages(stages):
            return
        parent = super(MimeRecognizer, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        attrs['mimerecognizer_buf'] = StringIO.StringIO()
        attrs['mimerecognizer_ignore'] = False
