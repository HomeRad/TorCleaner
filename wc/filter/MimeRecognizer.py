import cStringIO as StringIO
import mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'

import wc.filter
import wc.filter.Filter
import wc.magic


class MimeRecognizer (wc.filter.Filter.Filter):
    """Recognizes missing content type header of URLs request data"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_DECODE]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = []
    # which mime types this filter applies to
    mimelist = []

    def __init__ (self):
        """initialize image reducer flags"""
        super(MimeRecognizer, self).__init__()
        # minimal number of bytes before we start mime recognition
        self.minimal_size_bytes = 1024

    def filter (self, data, **attrs):
        """feed data to recognizer"""
        if not attrs.has_key('mimerecognizer_buf'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        if buf.tell() >= self.minimal_size_bytes:
            return self.recognize(buf, attrs)
        return ''

    def finish (self, data, **attrs):
        """feed data to recognizer"""
        if not attrs.has_key('mimerecognizer_buf'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        return self.recognize(buf, attrs)

    def recognize (self, buf, attrs):
        # note: recognizing a mime type fixes exploits like
        # CVE-2002-0025 and CVE-2002-0024
        try:
            mime = wc.magic.classify(buf)
            if not attrs['mime'].startswith(mime):
                wc.log.warn(wc.LOG_FILTER, "Adjusting MIME %r -> %r",
                            attrs['mime'], mime)
                attrs['headers']['data']['Content-Type'] = "%s\r" % mime
        except StandardError, msg:
            wc.log.exception(wc.LOG_FILTER, "Mime recognize error")
        data = buf.getvalue()
        buf.close()
        return data

    def get_attrs (self, url, headers):
        """initialize buffer"""
        d = super(MimeRecognizer, self).get_attrs(url, headers)
        d['mimerecognizer_buf'] = StringIO.StringIO()
        return d
