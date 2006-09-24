# -*- coding: iso-8859-1 -*-
# Copyright (c) 2000, Amit Patel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of Amit Patel nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
Gunzip.py, amitp@cs.stanford.edu, March 2000a

Implements the minimal amount of work needed to ungzip an input stream

Based on gzip.py in the standard Python distribution,
but exports a proxy4 encoding interface:
 - process(string) => return as much of the string as can be decoded
 - flush()        => return everything else
"""

import wc.log
import DeflateStream


class GunzipStream (DeflateStream.DeflateStream):
    """
    Stream filter ungzipp'ing data.
    """

    # Flags in the gzip header
    FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16

    def __init__ (self):
        """
        Initialize internal data buffer and flags.
        """
        super(GunzipStream, self).__init__()
        self.buf = ''
        self.header_seen = False
        self.error = False

    def __repr__ (self):
        """
        Object representation.
        """
        if self.closed:
            s = "closed"
        else:
            s = "open"
        return '<gunzip %s buflen=%d error=%s>' % \
                   (s, len(self.buf), self.error)

    def attempt_header_read (self):
        """
        Try to parse the header from buffer, and if we can, set flag.
        """
        if len(self.buf) < 10: # Incomplete fixed part of header
            return

        magic = self.buf[:2]
        if magic != '\037\213':
            wc.log.warn(wc.LOG_PROXY,
                        _("zlib error: not gzip format, disabling gunzip"))
            self.error = True
            return

        method = ord(self.buf[2])
        if method != 8:
            wc.log.warn(wc.LOG_PROXY,
                _("zlib error: unknown compression method, disabling gunzip"))
            self.error = True
            return

        flag = ord(self.buf[3])
        # Skip until byte 10
        s = self.buf[10:]

        if flag & self.FEXTRA:
            # Read & discard the extra field, if present
            if len(s) < 2:
                # Incomplete
                return
            xlen = ord(s[0])
            xlen += 256*ord(s[1])
            if len(s) < 2+xlen:
                # Incomplete
                return
            s = s[2+xlen:]

        if flag & self.FNAME:
            # Read and discard a null-terminated string containing the
            # filename
            i = s.find('\000')
            if i < 0:
                # Incomplete
                return
            s = s[i+1:]

        if flag & self.FCOMMENT:
            # Read and discard a null-terminated string containing a comment
            i = s.find('\000')
            if i < 0:
                # Incomplete
                return
            s = s[i+1:]

        if flag & self.FHCRC:
            # Read & discard the 16-bit header CRC
            if len(s) < 2:
                # Incomplete
                return
            s = s[2:]
        # We actually got through the header
        self.buf = s
        self.header_seen = True

    def process (self, s):
        """
        Gunzip data s.
        """
        if self.error:
            return s
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
        return super(GunzipStream, self).process(s)

    def flush (self):
        """
        Flush buffer data and return it.
        """
        if self.error:
            return self.buf
        if not self.header_seen:
            # We still haven't finished parsing the header .. oh well
            return self.buf
        else:
            return super(GunzipStream, self).flush()
