# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Recognize MIME types.
"""

import cStringIO as StringIO
import mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'

from .. import log, LOG_FILTER, magic
from . import Filter, STAGE_RESPONSE_DECODE


def is_preferred_mime(mime, origmime):
    """
    See if the newly found mime is preferred over the original one.
    @param mime: MIME type from magic module.
    @type mime: string
    @param origmime: original MIME type
    @type origmime: string
    """
    if mime == origmime:
        return False
    # keep specific applications
    if origmime.startswith("application/"):
        return False
    # New mime could be same as orig, but without appendix. Example:
    # mime="text/html", origmime="text/html; charset=UTF8"
    if origmime.startswith(mime+";"):
        return False
    # Sometimes text/html is recognized as text/plain.
    # And don't recognize html as xml
    if origmime.startswith("text/html") and  \
        (mime.startswith("text/plain") or
         mime.startswith("application/rss+xml") or
         mime.startswith("text/xml")):
        return False
    return True


class MimeRecognizer(Filter.Filter):
    """
    Recognizes missing or wrong content type header of URLs request data.
    """

    enable = True

    def __init__(self):
        """
        Initialize image reducer flags.
        """
        stages = [STAGE_RESPONSE_DECODE]
        super(MimeRecognizer, self).__init__(stages=stages)
        # minimal number of bytes to start mime recognition
        self.minimal_size_bytes = 5
        # sufficient number of bytes to start mime recognition
        self.sufficient_size_bytes = 1024

    def filter(self, data, attrs):
        """
        Feed data to recognizer.
        """
        if 'mimerecognizer_buf' not in attrs or \
           attrs.get('mimerecognizer_ignore'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        if buf.tell() >= self.sufficient_size_bytes:
            return self.recognize(buf, attrs)
        return ''

    def finish(self, data, attrs):
        """
        Feed data to recognizer.
        """
        if 'mimerecognizer_buf' not in attrs or \
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

    def recognize(self, buf, attrs):
        """Try to recognize MIME type and write Content-Type header."""
        # note: recognizing a mime type fixes exploits like
        # CVE-2002-0025 and CVE-2002-0024
        log.debug(LOG_FILTER, "MIME recognize %d bytes of data", buf.tell())
        try:
            mime = magic.classify(buf)
            log.debug(LOG_FILTER, "MIME recognized %r", mime)
            origmime = attrs['mime']
            if mime and origmime and is_preferred_mime(mime, origmime):
                log.info(LOG_FILTER, "Adjusting MIME %r -> %r at %r",
                            origmime, mime, attrs['url'])
                attrs['mime'] = mime
                attrs['headers']['data']['Content-Type'] = "%s\r" % mime
        except StandardError:
            log.warn(LOG_FILTER, "Mime recognize error at %r (%r)",
                        attrs['url'], buf.getvalue())
        data = buf.getvalue()
        buf.close()
        return data

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """Initialize buffer."""
        if not self.applies_to_stages(stages):
            return
        parent = super(MimeRecognizer, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        attrs['mimerecognizer_buf'] = StringIO.StringIO()
        attrs['mimerecognizer_ignore'] = False
