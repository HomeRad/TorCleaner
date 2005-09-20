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
Test chunked encoding.
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

from wc.proxy.ftests import ProxyTest, make_suite, HttpResponse


class ChunkedResponseTest (ProxyTest):

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def chunked (self, data, repeat=1, trailers=None):
        """
        Chunk-encode data.

        @param data: data to encode
        @type data: string
        @param repeat: how much chunks of this data to generate
        @type repeat: integer
        @param trailers: trailer lines to append (without CRLF)
        @type trailers: list of strings
        """
        if not data:
            repeat = 0
            self.body = ""
        else:
            self.body = data*repeat
        parts = []
        while repeat > 0:
            parts.append(hex(len(data))[2:])
            parts.append(data)
            repeat -= 1
        parts.append("0")
        if trailers:
            parts.extend(trailers)
        parts.extend(("", ""))
        return "\r\n".join(parts)

    def check_response_content (self, response):
        """
        Compare result with expected values.
        """
        self.assertEqual(response.content, self.body)


class test_chunked_1p1_0B_toClt (ChunkedResponseTest):
    """
    Chunked response with zero-size content to HTTP/1.1 client
    """
    def test_chunked_1p1_0B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("")


class test_chunked_1p1_1B_toClt (ChunkedResponseTest):
    """
    Chunked response with one 1-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_1B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a")


class test_chunked_1p1_100B_toClt (ChunkedResponseTest):
    """
    Chunked response with one 100-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_100B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*100)


class test_chunked_1p1_65535B_toClt (ChunkedResponseTest):
    """
    Chunked response with one 65535-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65535B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*65535)


class test_chunked_1p1_65536B_toClt (ChunkedResponseTest):
    """
    Chunked response with one 65536-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65536B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*65536)


class test_chunked_1p1_65537B_toClt (ChunkedResponseTest):
    """
    Chunked response with one 65537-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65537B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*65537)


class test_chunked_1p1_2x100B_toClt (ChunkedResponseTest):
    """
    Chunked response with two 100-Byte chunks to HTTP/1.1 client
    """

    def test_chunked_1p1_2x100B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*100, repeat=2)


class test_chunked_1p1_1025x100B_toClt (ChunkedResponseTest):
    """
    Chunked response with 1025 100-Byte chunks to HTTP/1.1 client
    """

    def test_chunked_1p1_1025x100B_toClt (self):
        self.start_test()

    def get_response_content (self):
        return self.chunked("a"*100, repeat=1025)


class test_chunked_1p1_trailer_11_1_announced_woutTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_announced_woutTe_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo",
        ]

    def get_response_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo"))


class test_chunked_1p1_lead0s_toClt (ChunkedResponseTest):
    """
    Chunked response with leading zeros in chunk size to HTTP/1.1 client.
    """

    def test_chunked_1p1_lead0s_toClt (self):
        self.start_test()

    def get_response_content (self):
        self.body = "imadoofus"
        data = "0000000000%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "0\r\n\r\n"
        return data


class test_chunked_1p1_last_3x0_toClt (ChunkedResponseTest):
    """
    Chunked response with 3 zeros in last chunk to HTTP/1.1 client.
    """

    def test_chunked_1p1_last_3x0_toClt (self):
        self.start_test()

    def get_response_content (self):
        self.body = "imadoofus"
        data = "%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "%s\r\n\r\n" % ("0"*3)
        return data


class test_chunked_1p1_last_65x0_toClt (ChunkedResponseTest):
    """
    Chunked response with 65 zeros in last chunk to HTTP/1.1 client.
    """

    def test_chunked_1p1_last_65x0_toClt (self):
        self.start_test()

    def get_response_content (self):
        self.body = "imadoofus"
        data = "%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "%s\r\n\r\n" % ("0"*65)
        return data


class test_chunked_1p1_badClen_toClt (ChunkedResponseTest):

    def test_chunked_1p1_badClen_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Content-Length: 177999999",
        ]

    def get_response_content (self):
        return self.chunked("a"*100)


def test_suite ():
    """
    Build and return a TestSuite.
    """
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())

