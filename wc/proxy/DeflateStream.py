# -*- coding: iso-8859-1 -*-
"""Implements the minimal amount of work needed to inflate an input stream
example url is http://groups.yahoo.com/
"""

import zlib


class DeflateStream (object):
    """Filter object unzip'ing all data"""

    def __init__ (self):
        """initialize unzipper"""
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        self.closed = False

    def __repr__ (self):
        """object representation"""
        return '<%s closed=%s>' % ('deflate', self.closed)

    def decode (self, s):
        """unzip given data s and return decompressed data"""
        return self.decompressor.decompress(s)

    def flush (self):
        """flush all buffered data and return it"""
        return self.decompressor.flush()
