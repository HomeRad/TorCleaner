# Implements the minimal amount of work needed to inflate an input stream
# example url is http://groups.yahoo.com/

import zlib

class DeflateStream:
    def __init__ (self):
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        self.closed = 0

    def decode (self, s):
        return self.decompressor.decompress(s)

    def flush (self):
        return self.decompressor.flush()

