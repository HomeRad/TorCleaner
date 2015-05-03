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
Implements the minimal amount of work needed to inflate an input stream.
Example url is http://groups.yahoo.com/.
"""

from ... import log, LOG_PROXY
import zlib


class DeflateStream (object):
    """
    Filter object unzip'ing all data.
    """

    def __init__ (self):
        """
        Initialize unzipper.
        """
        self.decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        self.closed = False
        self.error = False

    def __repr__ (self):
        """
        Object representation.
        """
        if self.closed:
            s = "closed"
        else:
            s = "open"
        return '<deflate %s>' % s

    def process (self, s):
        """
        Unzip given data s and return decompressed data.
        """
        if self.error:
            # don't decode whan an error has occured
            return s
        try:
            return self.decompressor.decompress(s)
        except zlib.error:
            import sys
            msg = str(sys.exc_info()[1])
            log.info(LOG_PROXY,
                        _("zlib error: %s, disabling deflate"), msg)
            self.error = True
            return s

    def flush (self):
        """
        Flush all buffered data and return it.
        """
        if self.error:
            return ""
        return self.decompressor.flush()

