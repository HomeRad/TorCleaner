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
Encoding_chunked, amitp@cs.stanford.edu, March 2000
Deal with Transfer-encoding: chunked [HTTP/1.1].

Grammar for a chunked-encoded message body:
Chunked-Body   = *chunk
                 last-chunk
                 trailer
                 CRLF

chunk          = chunk-size [ chunk-extension ] CRLF
                 chunk-data CRLF
chunk-size     = 1*HEX
last-chunk     = 1*("0") [ chunk-extension ] CRLF

chunk-extension= *( ";" chunk-ext-name [ "=" chunk-ext-val ] )
chunk-ext-name = token
chunk-ext-val  = token | quoted-string
chunk-data     = chunk-size(OCTET)
trailer        = *(entity-header CRLF)
"""

import re
import cStringIO as StringIO
import wc
import wc.log
import wc.http.header


match_bytes = re.compile(r"^(?P<bytes>[0-9a-fA-F]+)(;.+)?$").search


class UnchunkStream (object):
    """
    Stream filter for chunked transfer encoding
    States:
     - bytes_remaining is None:
       we're in the "need chunk size" state
     - bytes_remaining is not None:
       we're reading up to bytes_remaining elements of data
    """

    def __init__ (self):
        """
        Initialize internal buffers and flags.
        """
        self.buf = ''
        # Store chunk trailer for later use. Has to be a mutable object
        # for sharing between coders.
        self.trailer = StringIO.StringIO()
        self.bytes_remaining = None
        self.closed = False

    def __repr__ (self):
        """
        Representation of stream filter state.
        """
        if self.closed:
            s = "closed"
        else:
            s = "open"
        return '<unchunk %s buflen=%d bytes_remaining=%s>' % \
                  (s, len(self.buf), self.bytes_remaining)

    def process (self, s):
        """
        Unchunk given data s.
        """
        wc.log.debug(wc.LOG_NET, "chunked data %r", s)
        self.buf += s
        s = ''
        while self.buf and not self.closed:
            # Keep looking for alternating chunk lengths and chunk content
            if self.bytes_remaining is None:
                # We want to find a chunk length
                i = self.buf.find('\r\n')
                if i >= 0:
                    # We have a line; let's hope it's a chunk length
                    line = self.buf[:i].strip()
                    # Remove this line from the buffer
                    self.buf = self.buf[i+2:]
                    if line:
                        # NOTE: chunklen can be followed by ";.*"
                        mo = match_bytes(line)
                        if mo:
                            # chunklen is hex
                            self.bytes_remaining = int(mo.group('bytes'), 16)
                        else:
                            wc.log.warn(wc.LOG_PROXY,
                                        "invalid chunk size %r", line)
                            self.bytes_remaining = 0
                        #print 'chunk len:', self.bytes_remaining
                        if self.bytes_remaining == 0:
                            # End of stream
                            self.closed = True
                            # at this point, read trailer until a blank line
                            self.read_trailer()
                else:
                    break
            if self.bytes_remaining is not None:
                # We know how many bytes we need
                data = self.buf[:self.bytes_remaining]
                s += data
                self.buf = self.buf[self.bytes_remaining:]
                self.bytes_remaining -= len(data)
                assert self.bytes_remaining >= 0
                if self.bytes_remaining == 0:
                    # We reached the end of the chunk
                    self.bytes_remaining = None
        wc.log.debug(wc.LOG_NET, "decoded chunk %r", s)
        return s

    def read_trailer (self):
        i = self.buf.find('\r\n')
        if i >= 0:
            line = self.buf[:i].strip()
            if not line:
                self.buf = self.buf[i+2:]
                return
        # store trailer
        i = self.buf.find('\r\n\r\n')
        if i >= 0:
            self.trailer.write(self.buf[:i])
            self.buf = self.buf[i+4:]

    def flush (self):
        """
        Flush internal buffers and return flushed data.
        """
        s = self.buf
        self.buf = ''
        wc.log.debug(wc.LOG_NET, "flush chunk %r", s)
        return s
