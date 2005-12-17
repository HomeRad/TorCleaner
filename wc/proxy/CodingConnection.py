# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
Handle encoding and decoding.
"""

import cStringIO as StringIO
import wc
import wc.log
import wc.proxy.StatefulConnection
from wc.decorators import notimplemented


class CodingConnection (wc.proxy.StatefulConnection.StatefulConnection):
    """
    Connection storing a list of decoders and encoders.
    """

    def reset (self):
        """
        Reset the connection data and status.
        """
        super(CodingConnection, self).reset()
        # Handle each of these, left to right
        self.decoders = []
        self.encoders = []
        # Chunk trailer store
        self.chunktrailer = StringIO.StringIO()

    def flush_coders (self, coders, data=""):
        """
        Flush given de- or encoders.

        @param data: initial data to process (default: empty string)
        @ptype data: string
        @return: flushed data
        @rtype: string
        """
        while coders:
            assert wc.log.debug(wc.LOG_PROXY, "flush %s", coders[0])
            data = coders[0].process(data)
            data += coders[0].flush()
            del coders[0]
        return data

    @notimplemented
    def filter_headers (self, headers):
        """
        Filter HTTP headers.

        @param headers: the headers to filter
        @ptype headers: wc.http.header.WcMessage
        @return: filtered headers
        @rtype: wc.http.header.WcMessage
        """
        pass

    def write_trailer (self, data):
        """
        Store data of a chunk trailer.
        """
        self.chunktrailer.write(data)

    def handle_trailer (self):
        """
        Process a completed chunk trailer. This method must be called
        only once.
        """
        self.chunktrailer.seek(0)
        headers = wc.http.header.WcMessage(self.chunktrailer)
        # filter headers
        headers = self.filter_headers(headers)
        if headers:
            assert wc.log.debug(wc.LOG_PROXY,
                                "chunk trailer headers %s", headers)
        self.chunktrailer.close()
        return headers
