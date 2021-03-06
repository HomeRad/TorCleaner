# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
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

from ... import log, LOG_NET


def chunkenc(data):
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


class ChunkStream(object):
    """
    Stream filter for chunked transfer encoding
    """

    def __init__(self, trailerhandler):
        """
        Initialize closed flag and trailer handler.

        @param trailerhandler: a mutable trailer storage
        @ptype trailerhandler: object with get_headers() method
        """
        self.closed = False
        self.trailerhandler = trailerhandler

    def __repr__(self):
        """
        Representation of stream filter state.
        """
        if self.closed:
            s = "closed"
        else:
            s = "open"
        return '<chunk %s>' % s

    def process(self, s):
        """
        Chunk given data s.
        """
        s = chunkenc(s)
        log.debug(LOG_NET, "chunked %d bytes: %r", len(s), s)
        return s

    def get_trailer(self):
        """
        Construct HTTP header lines.
        """
        headers = self.trailerhandler.handle_trailer()
        if not headers:
            return ""
        return "".join(headers.headers)+"\r\n"

    def flush(self):
        """
        Write end-chunk and trailer.
        """
        s = "0\r\n"
        s += self.get_trailer()
        s += "\r\n"
        log.debug(LOG_NET, "flush chunked %d bytes: %r", len(s), s)
        return s
