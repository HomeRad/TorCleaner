# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Handle encoding and decoding.
"""

from cStringIO import StringIO
from .. import log, LOG_PROXY, decorators
from . import StatefulConnection
from ..http.header import WcMessage


class CodingConnection(StatefulConnection.StatefulConnection):
    """Connection storing a list of decoders and encoders."""

    def reset(self):
        """Reset the connection data and status."""
        super(CodingConnection, self).reset()
        # Handle each of these, left to right
        self.decoders = []
        self.encoders = []
        # Chunk trailer store
        self.chunktrailer = StringIO()

    def flush_coders(self, coders, data=""):
        """Flush given de- or encoders.

        @param data: initial data to process (default: empty string)
        @ptype data: string
        @return: flushed data
        @rtype: string
        """
        while coders:
            log.debug(LOG_PROXY, "flush %s", coders[0])
            data = coders[0].process(data)
            data += coders[0].flush()
            del coders[0]
        return data

    @decorators.notimplemented
    def filter_headers(self, headers):
        """Filter HTTP headers.

        @param headers: the headers to filter
        @ptype headers: WcMessage
        @return: filtered headers
        @rtype: WcMessage
        """
        pass

    def write_trailer(self, data):
        """Store data of a chunk trailer."""
        self.chunktrailer.write(data)

    def handle_trailer(self):
        """Process a completed chunk trailer. This method must be called
        only once."""
        self.chunktrailer.seek(0)
        headers = WcMessage(self.chunktrailer)
        # filter headers
        headers = self.filter_headers(headers)
        log.debug(LOG_PROXY, "chunk trailer headers %s", headers)
        self.chunktrailer.close()
        return headers
