# -*- coding: iso-8859-1 -*-
# Implements the minimal amount of work needed to inflate an input stream
# example url is http://groups.yahoo.com/

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import zlib

class DeflateStream (object):
    def __init__ (self):
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        self.closed = False


    def __repr__ (self):
        return '<%s closed=%s>'%('deflate', self.closed)


    def decode (self, s):
        return self.decompressor.decompress(s)


    def flush (self):
        return self.decompressor.flush()

