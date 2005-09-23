# -*- coding: iso-8859-1 -*-
# Copyright (c) 2005 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
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

import cStringIO as StringIO
import wc
import wc.log


def chunkenc (data):
    """
    Chunk-encode data.

    @param data: data to encode
    @type data: string
    @return: chunk-encoded data if data is non-empty, else an empty string
    @rtype: string
    """
    if data:
        return "\r\n".join([hex(len(data))[2:], data])
    return ""


class ChunkStream (object):
    """
    Stream filter for chunked transfer encoding
    """

    def __init__ (self, trailerhandler):
        """
        Initialize closed flag and trailer handler.

        @param trailerhandler: a mutable trailer storage
        @ptype trailerhandler: object with get_headers() method
        """
        self.closed = False
        self.trailerhandler = trailerhandler

    def __repr__ (self):
        """
        Representation of stream filter state.
        """
        if self.closed:
            s = "closed"
        else:
            s = "open"
        return '<chunk %s>' % s

    def process (self, s):
        """
        Chunk given data s.
        """
        s = chunkenc(s)
        wc.log.debug(wc.LOG_NET, "chunked data %r", s)
        return s

    def get_trailer (self):
        """
        Construct HTTP header lines.
        """
        headers = self.trailerhandler.handle_trailer()
        if not headers:
            return ""
        return "".join(headers.headers)+"\r\n"

    def flush (self):
        """
        Write end-chunk and trailer.
        """
        s = "0\r\n"
        s += self.get_trailer()
        s += "\r\n"
        return s
