# gunzip.py, amitp@cs.stanford.edu, March 2000a
#
# Implements the minimal amount of work needed to ungzip an input stream
#
# Based on gzip.py in the standard Python distribution,
# but exports a proxy4 encoding interface:
#      decode(string) => return as much of the string as can be decoded
#      flush()        => return everything else

# TEST CASE:
#    http://tv.excite.com/grid
from DeflateStream import DeflateStream

import zlib

class GunzipStream (DeflateStream):
    # Flags in the gzip header
    FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16
    
    def __init__ (self):
        DeflateStream.__init__(self)
        self.buf = ''
        self.header_seen = 0

    def attempt_header_read (self):
        "Try to parse the header from buffer, and if we can, set flag"
        if len(self.buf) < 10: # Incomplete fixed part of header
            return ''

        magic = self.buf[:2]
        if magic != '\037\213':
            raise zlib.error, 'not gzip format'

        method = ord(self.buf[2])
        if method != 8:
            raise zlib.error, 'unknown compression method'

        flag = ord(self.buf[3])
        # Skip until byte 10
        s = self.buf[10:]

        if flag & self.FEXTRA:
            # Read & discard the extra field, if present
            if len(s) < 2: return '' # Incomplete
            xlen = ord(s[0])
            xlen += 256*ord(s[1])
            if len(s) < 2+xlen: return '' # Incomplete
            s = s[2+xlen:]

        if flag & self.FNAME:
            # Read and discard a null-terminated string containing the filename
            i = s.find('\000')
            if i < 0: return '' # Incomplete
            s = s[i+1:]
            
        if flag & self.FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            i = s.find('\000')
            if i < 0: return '' # Incomplete
            s = s[i+1:]
            
        if flag & self.FHCRC:
            # Read & discard the 16-bit header CRC
            if len(s) < 2: return '' # Incomplete
            s = s[2:]

        # We actually got through the header
        self.buf = s
        self.header_seen = 1

    def decode (self, s):
        if not self.header_seen:
            # Try to parse the header
            self.buf += s
            s = ''
            self.attempt_header_read()
            if self.header_seen:
                # Put the rest of the buffer back into the string,
                # for zlib use
                s = self.buf
                self.buf = ''
            else:
                # We haven't finished parsing the header
                return ''

        # We have seen the header, so we can move on to zlib
        return DeflateStream.decode(self, s)

    def flush (self):
        if not self.header_seen:
            # We still haven't finished parsing the header .. oh well
            return ''
        else:
            return DeflateStream.flush(self)

