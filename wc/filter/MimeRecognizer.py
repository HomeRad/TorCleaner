import cStringIO as StringIO
import mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'

import wc.log
import wc.filter
import wc.filter.Filter
import wc.magic


class MimeRecognizer (wc.filter.Filter.Filter):
    """Recognizes missing content type header of URLs request data"""
    # which filter stages this filter applies to (see filter/__init__.py)
    stages = [wc.filter.STAGE_RESPONSE_DECODE]
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

    def filter (self, data, attrs):
        """feed data to recognizer"""
        if not attrs.has_key('mimerecognizer_buf') or \
           attrs.get('mimerecognizer_ignore'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        if buf.tell() >= self.minimal_size_bytes:
            return self.recognize(buf, attrs)
        return ''

    def finish (self, data, attrs):
        """feed data to recognizer"""
        if not attrs.has_key('mimerecognizer_buf') or \
           attrs.get('mimerecognizer_ignore'):
            return data
        buf = attrs['mimerecognizer_buf']
        if buf.closed:
            return data
        buf.write(data)
        return self.recognize(buf, attrs)

    def recognize (self, buf, attrs):
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
        except StandardError, msg:
            wc.log.exception(wc.LOG_FILTER, "Mime recognize error")
        data = buf.getvalue()
        buf.close()
        return data

    def get_attrs (self, url, localhost, stages, headers):
        """initialize buffer"""
        if not self.applies_to_stages(stages):
            return {}
        d = super(MimeRecognizer, self).get_attrs(url, localhost, stages, headers)
        d['mimerecognizer_buf'] = StringIO.StringIO()
        d['mimerecognizer_ignore'] = False
        return d
