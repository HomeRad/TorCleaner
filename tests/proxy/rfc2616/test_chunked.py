# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
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

from .. import ProxyTest


def chunk_size (data, extension):
    """
    Get chunk size of data with possible extension.

    @param data: data to chunk
    @ptype data: string
    @param extension: possible extension
    @ptype: string or None
    @return: hex-encoded length with possible extension
    @rtype: string
    """
    hexstr = hex(len(data))[2:]
    if extension:
        hexstr += extension
    return hexstr


class ChunkedTest (ProxyTest):
    """
    Base class for chunked requests and responses.
    """

    def chunked (self, data, repeat=1, trailers=None, extension=None):
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
            parts.append(chunk_size(data, extension))
            parts.append(data)
            repeat -= 1
        parts.append(chunk_size("", extension))
        if trailers:
            parts.extend(trailers)
        parts.extend(("", ""))
        return "\r\n".join(parts)


class ChunkedResponseTest (ChunkedTest):
    """
    Send a chunked response.
    """

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def check_response_content (self, response):
        """
        Compare result with expected values.
        """
        self.assertEqual(response.content, self.body)


class ChunkedRequestTest (ChunkedTest):
    """
    Send a chunked request.
    """

    def get_request_method (self):
        """
        Make a POST request since GET must not have content.
        """
        return "POST"

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        return [
            "Host: localhost:%d" % port,
            "Proxy-Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def check_request_content (self, request):
        """
        Compare result with expected values.
        """
        self.assertEqual(request.content, self.body)


########################## response tests #########################


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


class test_chunked_1p1_trailer_11_1_announced_withTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_announced_withTe_toClt (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = super(test_chunked_1p1_trailer_11_1_announced_withTe_toClt, self).get_request_headers(content)
        headers.append("TE: trailers")
        return headers

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


class test_chunked_1p1_trailer_11_1_surprisesurprise_woutTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 1 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_surprise_woutTe_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def get_response_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo"))


class test_chunked_1p1_trailer_11_1_surprise_withTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 1 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_surprise_withTe_toClt (self):
        self.start_test()

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
           "TE: trailers",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

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


class test_chunked_1p1_trailer_11_17_announced_woutTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 17 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_announced_woutTe_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_response_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo1"))
        self.assert_(response.has_header("Foo2"))
        self.assert_(response.has_header("Foo3"))
        self.assert_(response.has_header("Foo4"))
        self.assert_(response.has_header("Foo5"))
        self.assert_(response.has_header("Foo6"))
        self.assert_(response.has_header("Foo7"))
        self.assert_(response.has_header("Foo8"))
        self.assert_(response.has_header("Foo9"))
        self.assert_(response.has_header("Foo10"))
        self.assert_(response.has_header("Foo11"))
        self.assert_(response.has_header("Foo12"))
        self.assert_(response.has_header("Foo13"))
        self.assert_(response.has_header("Foo14"))
        self.assert_(response.has_header("Foo15"))
        self.assert_(response.has_header("Foo16"))
        self.assert_(response.has_header("Foo17"))


class test_chunked_1p1_trailer_11_17_announced_withTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 17 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_announced_withTe_toClt (self):
        self.start_test()

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
           "TE: trailers",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_response_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo1"))
        self.assert_(response.has_header("Foo2"))
        self.assert_(response.has_header("Foo3"))
        self.assert_(response.has_header("Foo4"))
        self.assert_(response.has_header("Foo5"))
        self.assert_(response.has_header("Foo6"))
        self.assert_(response.has_header("Foo7"))
        self.assert_(response.has_header("Foo8"))
        self.assert_(response.has_header("Foo9"))
        self.assert_(response.has_header("Foo10"))
        self.assert_(response.has_header("Foo11"))
        self.assert_(response.has_header("Foo12"))
        self.assert_(response.has_header("Foo13"))
        self.assert_(response.has_header("Foo14"))
        self.assert_(response.has_header("Foo15"))
        self.assert_(response.has_header("Foo16"))
        self.assert_(response.has_header("Foo17"))


class test_chunked_1p1_trailer_11_17_surprise_woutTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 17 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_surprise_woutTe_toClt (self):
        self.start_test()

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def get_response_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo1"))
        self.assert_(response.has_header("Foo2"))
        self.assert_(response.has_header("Foo3"))
        self.assert_(response.has_header("Foo4"))
        self.assert_(response.has_header("Foo5"))
        self.assert_(response.has_header("Foo6"))
        self.assert_(response.has_header("Foo7"))
        self.assert_(response.has_header("Foo8"))
        self.assert_(response.has_header("Foo9"))
        self.assert_(response.has_header("Foo10"))
        self.assert_(response.has_header("Foo11"))
        self.assert_(response.has_header("Foo12"))
        self.assert_(response.has_header("Foo13"))
        self.assert_(response.has_header("Foo14"))
        self.assert_(response.has_header("Foo15"))
        self.assert_(response.has_header("Foo16"))
        self.assert_(response.has_header("Foo17"))


class test_chunked_1p1_trailer_11_17_surprise_withTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 11Byte chunk and with 17 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_surprise_withTe_toClt (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = super(test_chunked_1p1_trailer_11_17_surprise_withTe_toClt, self).get_request_headers(content)
        headers.append("TE: trailers")
        return headers

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_response_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo1"))
        self.assert_(response.has_header("Foo2"))
        self.assert_(response.has_header("Foo3"))
        self.assert_(response.has_header("Foo4"))
        self.assert_(response.has_header("Foo5"))
        self.assert_(response.has_header("Foo6"))
        self.assert_(response.has_header("Foo7"))
        self.assert_(response.has_header("Foo8"))
        self.assert_(response.has_header("Foo9"))
        self.assert_(response.has_header("Foo10"))
        self.assert_(response.has_header("Foo11"))
        self.assert_(response.has_header("Foo12"))
        self.assert_(response.has_header("Foo13"))
        self.assert_(response.has_header("Foo14"))
        self.assert_(response.has_header("Foo15"))
        self.assert_(response.has_header("Foo16"))
        self.assert_(response.has_header("Foo17"))


class test_chunked_1p1_trailer_0_1_announced_woutTe_toClt (ChunkedResponseTest):
    """
    Chunked response with one 0-Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_0_1_announced_woutTe_toClt (self):
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
        return self.chunked("", trailers=trailers)

    def check_response_headers (self, response):
        self.assert_(response.has_header("Foo"))


class test_chunked_1p1_nameExt_toClt (ChunkedResponseTest):
    """
    Chunked response with a chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_nameExt_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ";foo"
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_valueExt_toClt (ChunkedResponseTest):
    """
    Chunked response with a valued chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_valueExt_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ";foo=bar"
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_spacesValExt_toClt (ChunkedResponseTest):
    """
    Chunked response with a chunk-extension with spaces token sent to
    an HTTP/1.1 client.
    """

    def test_chunked_1p1_spacesValExt_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ";foo =  bar "
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_quotedValExt_toClt (ChunkedResponseTest):
    """
    Chunked response with a quoted chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_quotedValExt_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ';foo="a=b0xffff==abar"'
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_longValExt_16385_toClt (ChunkedResponseTest):
    """
    Chunked response with a 16385 Byte long chunk-extension token
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_longValExt_16385_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ';foo='+("a"*16385)
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_longQValExt_16385_toClt (ChunkedResponseTest):
    """
    Chunked response with a 16385 Byte long quoted chunk-extension token
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_longQValExt_16385_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ';foo="'+("="*16385)+'"'
        return self.chunked("a"*10, extension=extension)


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


class test_chunked_1p1_0B_ext_toClt (ChunkedResponseTest):
    """
    Chunked response with 0 Bytes of content and a chunk-extension
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_0B_ext_toClt (self):
        self.start_test()

    def get_response_content (self):
        extension = ';foo=bar'
        return self.chunked("", extension=extension)


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


########################## request tests #########################


class test_chunked_1p1_0B_toSrv (ChunkedRequestTest):
    """
    Chunked request with zero-size content to HTTP/1.1 client
    """
    def test_chunked_1p1_0B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("")


class test_chunked_1p1_1B_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 1-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_1B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a")


class test_chunked_1p1_100B_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 100-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_100B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*100)


class XXXtest_chunked_1p1_65535B_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 65535-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65535B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*65535)


class XXXtest_chunked_1p1_65536B_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 65536-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65536B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*65536)


class XXXtest_chunked_1p1_65537B_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 65537-Byte chunk to HTTP/1.1 client
    """

    def test_chunked_1p1_65537B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*65537)


class test_chunked_1p1_2x100B_toSrv (ChunkedRequestTest):
    """
    Chunked request with two 100-Byte chunks to HTTP/1.1 client
    """

    def test_chunked_1p1_2x100B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*100, repeat=2)


class XXXtest_chunked_1p1_1025x100B_toSrv (ChunkedRequestTest):
    """
    Chunked request with 1025 100-Byte chunks to HTTP/1.1 client
    """

    def test_chunked_1p1_1025x100B_toSrv (self):
        self.start_test()

    def get_request_content (self):
        return self.chunked("a"*100, repeat=1025)


class XXXtest_chunked_1p1_trailer_11_1_announced_woutTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_announced_woutTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo",
        ]

    def get_request_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo"))


class XXXtest_chunked_1p1_trailer_11_1_announced_withTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_announced_withTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = super(test_chunked_1p1_trailer_11_1_announced_withTe_toSrv, self).get_request_headers(content)
        headers.append("TE: trailers")
        return headers

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo",
        ]

    def get_request_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo"))


class XXXtest_chunked_1p1_trailer_11_1_surprise_woutTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 1 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_surprise_woutTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def get_request_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo"))


class XXXtest_chunked_1p1_trailer_11_1_surprise_withTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 1 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_1_surprise_withTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
           "TE: trailers",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo",
        ]

    def get_request_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo"))


class XXXtest_chunked_1p1_trailer_11_17_announced_woutTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 17 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_announced_woutTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_request_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo1"))
        self.assert_(request.has_header("Foo2"))
        self.assert_(request.has_header("Foo3"))
        self.assert_(request.has_header("Foo4"))
        self.assert_(request.has_header("Foo5"))
        self.assert_(request.has_header("Foo6"))
        self.assert_(request.has_header("Foo7"))
        self.assert_(request.has_header("Foo8"))
        self.assert_(request.has_header("Foo9"))
        self.assert_(request.has_header("Foo10"))
        self.assert_(request.has_header("Foo11"))
        self.assert_(request.has_header("Foo12"))
        self.assert_(request.has_header("Foo13"))
        self.assert_(request.has_header("Foo14"))
        self.assert_(request.has_header("Foo15"))
        self.assert_(request.has_header("Foo16"))
        self.assert_(request.has_header("Foo17"))


class XXXtest_chunked_1p1_trailer_11_17_announced_withTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 17 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_announced_withTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
           "TE: trailers",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_request_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo1"))
        self.assert_(request.has_header("Foo2"))
        self.assert_(request.has_header("Foo3"))
        self.assert_(request.has_header("Foo4"))
        self.assert_(request.has_header("Foo5"))
        self.assert_(request.has_header("Foo6"))
        self.assert_(request.has_header("Foo7"))
        self.assert_(request.has_header("Foo8"))
        self.assert_(request.has_header("Foo9"))
        self.assert_(request.has_header("Foo10"))
        self.assert_(request.has_header("Foo11"))
        self.assert_(request.has_header("Foo12"))
        self.assert_(request.has_header("Foo13"))
        self.assert_(request.has_header("Foo14"))
        self.assert_(request.has_header("Foo15"))
        self.assert_(request.has_header("Foo16"))
        self.assert_(request.has_header("Foo17"))


class XXXtest_chunked_1p1_trailer_11_17_surprise_woutTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 17 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_surprise_woutTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
        ]

    def get_request_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo1"))
        self.assert_(request.has_header("Foo2"))
        self.assert_(request.has_header("Foo3"))
        self.assert_(request.has_header("Foo4"))
        self.assert_(request.has_header("Foo5"))
        self.assert_(request.has_header("Foo6"))
        self.assert_(request.has_header("Foo7"))
        self.assert_(request.has_header("Foo8"))
        self.assert_(request.has_header("Foo9"))
        self.assert_(request.has_header("Foo10"))
        self.assert_(request.has_header("Foo11"))
        self.assert_(request.has_header("Foo12"))
        self.assert_(request.has_header("Foo13"))
        self.assert_(request.has_header("Foo14"))
        self.assert_(request.has_header("Foo15"))
        self.assert_(request.has_header("Foo16"))
        self.assert_(request.has_header("Foo17"))


class XXXtest_chunked_1p1_trailer_11_17_surprise_withTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 11Byte chunk and with 17 surprise header(s)
    in the trailer sent to an HTTP/1.1 client that did send TE: trailers.
    """

    def test_chunked_1p1_trailer_11_17_surprise_withTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        headers = super(test_chunked_1p1_trailer_11_17_surprise_withTe_toSrv, self).get_request_headers(content)
        headers.append("TE: trailers")
        return headers

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo1",
            "Trailer: foo2",
            "Trailer: foo3",
            "Trailer: foo4",
            "Trailer: foo5",
            "Trailer: foo6",
            "Trailer: foo7",
            "Trailer: foo8",
            "Trailer: foo9",
            "Trailer: foo10",
            "Trailer: foo11",
            "Trailer: foo12",
            "Trailer: foo13",
            "Trailer: foo14",
            "Trailer: foo15",
            "Trailer: foo16",
            "Trailer: foo17",
        ]

    def get_request_content (self):
        trailers = [
            "Foo1: bar",
            "Foo2: bar",
            "Foo3: bar",
            "Foo4: bar",
            "Foo5: bar",
            "Foo6: bar",
            "Foo7: bar",
            "Foo8: bar",
            "Foo9: bar",
            "Foo10: bar",
            "Foo11: bar",
            "Foo12: bar",
            "Foo13: bar",
            "Foo14: bar",
            "Foo15: bar",
            "Foo16: bar",
            "Foo17: bar",
        ]
        return self.chunked("a"*11, trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo1"))
        self.assert_(request.has_header("Foo2"))
        self.assert_(request.has_header("Foo3"))
        self.assert_(request.has_header("Foo4"))
        self.assert_(request.has_header("Foo5"))
        self.assert_(request.has_header("Foo6"))
        self.assert_(request.has_header("Foo7"))
        self.assert_(request.has_header("Foo8"))
        self.assert_(request.has_header("Foo9"))
        self.assert_(request.has_header("Foo10"))
        self.assert_(request.has_header("Foo11"))
        self.assert_(request.has_header("Foo12"))
        self.assert_(request.has_header("Foo13"))
        self.assert_(request.has_header("Foo14"))
        self.assert_(request.has_header("Foo15"))
        self.assert_(request.has_header("Foo16"))
        self.assert_(request.has_header("Foo17"))


class XXXtest_chunked_1p1_trailer_0_1_announced_woutTe_toSrv (ChunkedRequestTest):
    """
    Chunked request with one 0-Byte chunk and with 1 announced header(s)
    in the trailer sent to an HTTP/1.1 client that did not send TE: trailers.
    """

    def test_chunked_1p1_trailer_0_1_announced_woutTe_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Trailer: foo",
        ]

    def get_request_content (self):
        trailers = [
            "Foo: bar",
        ]
        return self.chunked("", trailers=trailers)

    def check_request_headers (self, request):
        self.assert_(request.has_header("Foo"))


class test_chunked_1p1_nameExt_toSrv (ChunkedRequestTest):
    """
    Chunked request with a chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_nameExt_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ";foo"
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_valueExt_toSrv (ChunkedRequestTest):
    """
    Chunked request with a valued chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_valueExt_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ";foo=bar"
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_spacesValExt_toSrv (ChunkedRequestTest):
    """
    Chunked request with a chunk-extension with spaces token sent to
    an HTTP/1.1 client.
    """

    def test_chunked_1p1_spacesValExt_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ";foo =  bar "
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_quotedValExt_toSrv (ChunkedRequestTest):
    """
    Chunked request with a quoted chunk-extension token sent to an HTTP/1.1
    client.
    """

    def test_chunked_1p1_quotedValExt_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ';foo="a=b0xffff==abar"'
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_longValExt_16385_toSrv (ChunkedRequestTest):
    """
    Chunked request with a 16385 Byte long chunk-extension token
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_longValExt_16385_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ';foo='+("a"*16385)
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_longQValExt_16385_toSrv (ChunkedRequestTest):
    """
    Chunked request with a 16385 Byte long quoted chunk-extension token
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_longQValExt_16385_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ';foo="'+("="*16385)+'"'
        return self.chunked("a"*10, extension=extension)


class test_chunked_1p1_lead0s_toSrv (ChunkedRequestTest):
    """
    Chunked request with leading zeros in chunk size to HTTP/1.1 client.
    """

    def test_chunked_1p1_lead0s_toSrv (self):
        self.start_test()

    def get_request_content (self):
        self.body = "imadoofus"
        data = "0000000000%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "0\r\n\r\n"
        return data


class test_chunked_1p1_0B_ext_toSrv (ChunkedRequestTest):
    """
    Chunked request with 0 Bytes of content and a chunk-extension
    sent to an HTTP/1.1 client.
    """

    def test_chunked_1p1_0B_ext_toSrv (self):
        self.start_test()

    def get_request_content (self):
        extension = ';foo=bar'
        return self.chunked("", extension=extension)


class test_chunked_1p1_last_3x0_toSrv (ChunkedRequestTest):
    """
    Chunked request with 3 zeros in last chunk to HTTP/1.1 client.
    """

    def test_chunked_1p1_last_3x0_toSrv (self):
        self.start_test()

    def get_request_content (self):
        self.body = "imadoofus"
        data = "%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "%s\r\n\r\n" % ("0"*3)
        return data


class test_chunked_1p1_last_65x0_toSrv (ChunkedRequestTest):
    """
    Chunked request with 65 zeros in last chunk to HTTP/1.1 client.
    """

    def test_chunked_1p1_last_65x0_toSrv (self):
        self.start_test()

    def get_request_content (self):
        self.body = "imadoofus"
        data = "%s\r\n" % hex(len(self.body))[2:]
        data += "%s\r\n" % self.body
        data += "%s\r\n\r\n" % ("0"*65)
        return data


class XXXtest_chunked_1p1_badClen_toSrv (ChunkedRequestTest):

    def test_chunked_1p1_badClen_toSrv (self):
        self.start_test()

    def get_request_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Connection: close",
            "Transfer-Encoding: chunked",
            "Content-Length: 177999999",
        ]

    def get_request_content (self):
        return self.chunked("a"*100)
