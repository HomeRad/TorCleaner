# -*- coding: iso-8859-1 -*-
# encoding_chunked, amitp@cs.stanford.edu, March 2000
#
# Deal with Transfer-encoding: chunked [HTTP/1.1]

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

# TEST CASE:
#    http://www.apache.org/
from wc.log import *

import re
match_bytes = re.compile(r"^(?i)(?P<bytes>[0-9a-f]+)(;.+)?$").search

class UnchunkStream (object):
    # States:
    #   if bytes_remaining is None:
    #      we're in the "need chunk size" state
    #   else:
    #      we're reading up to bytes_remaining elements of data
    def __init__ (self):
        self.buf = ''
        self.bytes_remaining = None
        self.closed = False


    def decode (self, s):
        debug(PROXY, "Proxy: chunked data %s", `s`)
        self.buf += s
        s = ''

        while self.buf and not self.closed:
            # Keep looking for alternating chunk lengths and chunk content
            if self.bytes_remaining is None:
                # We want to find a chunk length
                i = self.buf.find('\n')
                if i >= 0:
                    # We have a line; let's hope it's a chunk length
                    line = self.buf[:i].strip()
                    # Remove this line from the buffer
                    self.buf = self.buf[i+1:]
                    if line:
                        # NOTE: chunklen can be followed by ";.*"
                        mo = match_bytes(line)
                        if mo:
                            # chunklen is hex
                            self.bytes_remaining = int(mo.group('bytes'), 16)
                        else:
                            warn(PROXY, "invalid chunk size %s", `line`)
                            self.bytes_remaining = 0
                        #print 'chunk len:', self.bytes_remaining
                        if self.bytes_remaining == 0:
                            # End of stream
                            self.closed = True
                            # XXX: at this point, we should read
                            # footers until we get to a blank line
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
        debug(PROXY, "Proxy: decoded chunk %s", `s`)
        return s


    def flush (self):
        s = self.buf.strip()
        self.buf = ''
        return s
