# -*- coding: iso-8859-1 -*-
# gunzip.py, amitp@cs.stanford.edu, March 2000a
#
# Implements the minimal amount of work needed to ungzip an input stream
#
# Based on gzip.py in the standard Python distribution,
# but exports a proxy4 encoding interface:
#      decode(string) => return as much of the string as can be decoded
#      flush()        => return everything else

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

# TEST CASE:
#    http://tv.excite.com/grid

# Changes: fall back to non-gzip on error to defeat b0rked servers

from DeflateStream import DeflateStream
from wc import i18n
from wc.log import *

class GunzipStream (DeflateStream):
    # Flags in the gzip header
    FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16

    def __init__ (self):
        super(GunzipStream, self).__init__()
        self.buf = ''
        self.header_seen = False
        self.error = False


    def attempt_header_read (self):
        "Try to parse the header from buffer, and if we can, set flag"
        if len(self.buf) < 10: # Incomplete fixed part of header
            return

        magic = self.buf[:2]
        if magic != '\037\213':
            warn(PROXY, i18n._("zlib error: not gzip format, disabling gunzip"))
            self.error = True
            return

        method = ord(self.buf[2])
        if method != 8:
            warn(PROXY, i18n._("zlib error: unknown compression method, disabling gunzip"))
            self.error = True
            return

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
            if i < 0: return # Incomplete
            s = s[i+1:]

        if flag & self.FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            i = s.find('\000')
            if i < 0: return # Incomplete
            s = s[i+1:]

        if flag & self.FHCRC:
            # Read & discard the 16-bit header CRC
            if len(s) < 2: return # Incomplete
            s = s[2:]

        # We actually got through the header
        self.buf = s
        self.header_seen = True


    def decode (self, s):
        if self.error: return s
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
        return super(GunzipStream, self).decode(s)


    def flush (self):
        if self.error: return self.buf
        if not self.header_seen:
            # We still haven't finished parsing the header .. oh well
            return self.buf
        else:
            return super(GunzipStream, self).flush()
