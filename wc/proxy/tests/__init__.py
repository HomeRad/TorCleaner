# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
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
Basic proxy test classes and methods.

Example test for a HEAD request:
class test_xyz (ProxyTest):
    "check HEAD request"

    def test_xyz (self):
        self.start_test()

    # now override test methods

    def get_response_method (self):
        return "HEAD"

    def check_response_content (self, response):
        # response must not have content
        self.assert_(not response.content)

#And the test suite method:
def test_suite ():
    "Build and return a TestSuite."
    prefix = __name__.split(".")[-1]
    return make_suite(prefix, globals())

"""

import cStringIO as StringIO
import rfc822
import unittest
import socket
import sys
import BaseHTTPServer
import tests
import wc.dummy
import wc.proxy
import wc.proxy.decoder.UnchunkStream


_debug = 0
if _debug:
    def debug (msg):
        print >> sys.stderr, "TEST", msg
else:
    debug = wc.dummy.Dummy()

###################### utility functions ######################

class TrailerHandler (object):
    """
    Store chunk trailer for chunked encoding.
    """

    def __init__ (self, headers):
        """
        Init trailer store and set self.headers.
        """
        self.chunktrailer = StringIO.StringIO()
        self.headers = headers

    def write_trailer (self, data):
        """
        Write trailer data.
        """
        self.chunktrailer.write(data)

    def handle_trailer (self):
        """
        Parse trailer headers and write them into self.headers.
        """
        self.chunktrailer.seek(0)
        headers = wc.http.header.WcMessage(self.chunktrailer)
        self.chunktrailer.close()
        for name in headers:
            for value in headers.getheaders(name):
                self.headers.append("%s: %s" % (name, value))


def decode_transfer (encoding, data, handler):
    """
    Decode data according to given transfer encoding. Optional the header
    list is updated since the "chunked" encoding can have additional
    header lines.

    @param encoding: value of Transfer-Encoding header
    @ptype encoding: string
    @param data: data to decode
    @ptype data: string
    @param headers: header lines to extend (mutable object, side effect)
    @ptype headers: list of strings
    @return: encoded data
    @rtype: string
    """
    if encoding == "chunked":
        unchunk = wc.proxy.decoder.UnchunkStream.UnchunkStream(handler)
        data = unchunk.process(data)
        data += unchunk.flush()
    else:
        raise ValueError("Unknown transfer encoding %r" % encoding)
    return data


def decode_content (encoding, data):
    """
    Decode data with given content-encoding.
    """
    if encoding == "gzip":
        import gzip
        buf = StringIO.StringIO(data)
        fp = gzip.GzipFile("", "rb", 9, buf)
        data = fp.read()
        fp.close()
        buf.close()
    elif encoding == "compress":
        import zlib
        data = zlib.decompress(data)
    elif encoding == "identity":
        pass
    else:
        raise ValueError("Unknown content encoding %r" % encoding)
    return data


def socket_send (sock, data):
    """
    Send data to socket.
    """
    sock.sendall(data)
    debug("Socket sent %d bytes: %r" % (len(data), data))


def socket_read (sock):
    """
    Read data from socket until no more data is available.
    """
    data = ""
    while wc.proxy.readable_socket(sock):
        s = sock.recv(8192)
        if not s:
            break
        data += s
    debug("Socket read %d bytes: %r" % (len(data), data))
    return data


def socketfile_read (sock):
    """
    Read data from socket until no more data is available.
    """
    data = ""
    while wc.proxy.readable_socket(sock):
        s = sock.read(1)
        if not s:
            break
        data += s
    debug("Socket file read %d bytes: %r" % (len(data), data))
    return data + sock._rbuf


class HttpData (object):
    """
    Store HTTP data.
    """

    def __init__ (self, headers, content=None):
        """
        Set headers and content variables.
        """
        self.headers = headers
        self.content = content

    def has_header (self, name):
        """
        Test if header with given name is stored.
        """
        return self.num_headers(name) > 0

    def num_headers (self, name):
        """
        Count number of headers with given name.
        """
        num = 0
        # HTTP headers are case insensitive
        key = name.lower()
        for header in self.headers:
            if header.lower().startswith("%s:" % key):
                num += 1
        return num

    def get_header (self, name):
        """
        Get first header value with given name.
        @raise: KeyError if header is not found
        """
        # HTTP headers are case insensitive
        key = name.lower()
        for header in self.headers:
            if header.lower().startswith("%s:" % key):
                return header.split(":", 1)[1].strip()
        raise KeyError(name)


class HttpRequest (HttpData):
    """
    Store HTTP request data.
    """

    def __init__ (self, method, uri, version, headers, content=None):
        """
        @param method: request method
        @type method: string
        @param uri: request URI
        @type method: string
        @param version: HTTP version (major,minor)
        @type version: tuple (int, int)
        @param headers: list of header lines (without CRLF)
        @type headers: list of strings
        @param content: body content
        @type content: string or None
        """
        self.method = method
        self.uri = uri
        self.version = version
        super(HttpRequest, self).__init__(headers, content=content)


class HttpResponse (HttpData):
    """
    Store HTTP response data.
    """

    def __init__ (self, version, status, msg, headers, content=None):
        """
        @param version: HTTP version (major,minor)
        @type version: tuple (int, int)
        @param status: HTTP status code
        @type status: int
        @param msg: HTTP status message
        @type msg: string
        @param headers: list of header lines (without CRLF)
        @type headers: list of strings
        @param content: body content
        @type content: string or None
        """
        self.version = version
        self.status = status
        self.msg = msg
        super(HttpResponse, self).__init__(headers, content=content)


class HttpClient (object):
    """
    Simple minded HTTP client class.
    """

    def __init__ (self):
        """
        Initial the socket is not connected
        """
        self.socket = None

    def connect (self, addr):
        """
        Connect to given address.
        """
        debug("Client connect to %s" % str(addr))
        self.socket = socket.socket()
        self.socket.connect(addr)

    def connected (self):
        """
        Check if this client is already connected.
        """
        return self.socket != None

    def send_data (self, data):
        """
        Send complete data to socket.
        """
        debug("Client send")
        socket_send(self.socket, data)

    def read_data (self):
        """
        Read until no more data is available.
        """
        debug("Client read")
        return socket_read(self.socket)


class HttpServer (BaseHTTPServer.HTTPServer):
    """
    Custom HTTP server class.
    """

    def handle_request(self):
        """
        Handle one request, possibly blocking. Exceptions are raised
        again for the test suite to handle.
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.close_request(request)
                raise

    def handle_error(self, request, client_address):
        """
        Suppress error printing.
        """
        pass


class HttpRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Custom HTTP request handler.
    """

    def handle_one_request (self):
        """
        Read one request and parse it. Then let the TestCase class
        check the request and construct the response which is sent back.
        """
        debug("Server handle one request...")
        self.raw_requestline = self.rfile.readline()
        if not self.raw_requestline:
            self.close_connection = 1
            return
        if not self.parse_request():
            # an error code has been sent, just exit
            return
        self.server.tester.check_request(self.get_request())
        response = self.server.tester.get_response()
        data = self.server.tester.construct_response_data(response)
        self.wfile.write(data)
        debug("... ok.")

    def log_message (self, format, *args):
        """
        Suppress request/error logging.
        """
        pass

    def get_request (self):
        """
        Get HttpRequest from internal data
        """
        method = self.command
        uri = self.path
        vparts = self.request_version.split('/', 1)[1].split(".")
        version = (int(vparts[0]), int(vparts[1]))
        headers = [line[:-1] for line in self.headers.headers]
        if self.headers.has_key("Content-Length"):
            clen = int(self.headers["Content-Length"])
            data = self.rfile.read(clen)
        else:
            data = socketfile_read(self.rfile)
        if "Transfer-Encoding" in self.headers:
            handler = TrailerHandler(headers)
            enctype = self.headers["Transfer-Encoding"]
            data = decode_transfer(enctype, data, handler)
            handler.handle_trailer()
        if "Content-Encoding" in self.headers:
            enctype = self.headers["Content-Encoding"]
            data = decode_content(enctype, data)
        return HttpRequest(method, uri, version, headers, content=data)


################ Proxy tests ######################

class ProxyTest (tests.StandardTest):
    """
    Basic proxy test case. Subclasses have complete control over
    request or response data by overriding the
    get_{request,response}_* methods, or if needed the methods
    construct_{request,response}_*.
    The test_*() method can just call start_test() to start sending
    the request and reading the response.
    """

    # the proxy to test must be started
    needed_resources = ['proxy']

    def setUp (self):
        """
        Set up the test case and check the proxy resource.
        """
        super(ProxyTest, self).setUp()
        self.check_resources(self.needed_resources)

    def start_client (self):
        """
        Start a HTTP client which is ready for use.
        @return: http client
        @rtype: HttpClient
        """
        debug("Start client")
        return HttpClient()

    def start_server (self):
        """
        Start a HTTP server which is ready for use.
        @return: http server
        @rtype: BaseHTTPServer.HTTPServer
        """
        port = 8000
        server_address = ('', port)
        debug("Start server on %d" % port)
        HandlerClass = HttpRequestHandler
        HandlerClass.protocol_version = "HTTP/1.1"
        ServerClass = HttpServer
        httpd = ServerClass(server_address, HandlerClass)
        httpd.tester = self
        return httpd

    def get_request (self):
        """
        Build a HTTP request from individual get_request_* methods.
        @return: HTTP request
        @rtype: HttpRequest
        """
        method = self.get_request_method()
        uri = self.get_request_uri()
        version = self.get_request_version()
        content = self.get_request_content()
        headers = self.get_request_headers(content)
        return HttpRequest(method, uri, version, headers, content=content)

    def get_request_method (self):
        """
        Get HTTP request method; default is 'GET'.
        """
        return "GET"

    def get_request_uri (self):
        """
        Get HTTP request URI; default is '/'.
        """
        return "/"

    def get_request_version (self):
        """
        Get HTTP request version; default is 1.1.
        """
        return (1, 1)

    def get_request_content (self):
        """
        Get HTTP request content; default is an empty string.
        Note that some request methods do not allow a non-empty
        content to be set (ie. the GET method).
        """
        return ""

    def get_request_headers (self, content):
        """
        Get request headers; default are a Host: and a Proxy-Connection:
        header, and a Content-Length: header if a non-empty request
        content has been given.
        """
        port = self.server.socket.getsockname()[1]
        headers = [
           "Host: localhost:%d" % port,
           "Proxy-Connection: close",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def construct_request_data (self, request):
        """
        Construct valid HTTP request data string.
        """
        lines = []
        version = "HTTP/%d.%d" % request.version
        lines.append("%s %s %s" % (request.method, request.uri, version))
        lines.extend(request.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if request.content:
            data += request.content
        return data

    def check_request (self, request):
        """
        Check individual parts of the request with check_request_*
        methods.
        """
        self.assert_(request is not None)
        self.check_request_method(request)
        self.check_request_uri(request)
        self.check_request_version(request)
        self.check_request_headers(request)
        self.check_request_content(request)

    def check_request_method (self, request):
        """
        Check HTTP request method.
        """
        self.assertEquals(request.method, self.get_request_method())

    def check_request_uri (self, request):
        """
        Check HTTP request URI.
        """
        self.assertEquals(request.uri, self.get_request_uri())

    def check_request_version (self, request):
        """
        Check HTTP request version.
        """
        self.assertEquals(request.version, self.get_request_version())

    def check_request_headers (self, request):
        """
        Check HTTP request headers.
        """
        pass

    def check_request_content (self, request):
        """
        Check HTTP request content.
        """
        self.assertEquals(request.content, self.get_request_content())

    def get_response (self):
        """
        Build a HTTP response from individual get_response_* methods.
        @return: HTTP response
        @rtype: HttpResponse
        """
        version = self.get_response_version()
        status = self.get_response_status()
        msg = self.get_response_message(status)
        content = self.get_response_content()
        headers = self.get_response_headers(content)
        return HttpResponse(version, status, msg, headers, content=content)

    def get_response_version (self):
        """
        Get HTTP response version; default (1, 1).
        @return: HTTP version
        @rtype: tuple of two integers
        """
        return (1, 1)

    def get_response_status (self):
        """
        Get HTTP response status; default 200.
        @return: status
        @rtype: integer
        """
        return 200

    def get_response_message (self, status):
        """
        Get HTTP response message; default 'Ok'.
        """
        return "Ok"

    def get_response_content (self):
        """
        Get HTTP response content; default 'hui'.
        """
        return "hui"

    def get_response_headers (self, content):
        """
        Get HTTP response headers; default are a Content-Type: text/plain
        and a Content-Length: header if content was non-empty.
        """
        headers = [
            "Content-Type: text/plain",
        ]
        if content:
            headers.append("Content-Length: %d" % len(content))
        return headers

    def construct_response_data (self, response):
        """
        Construct a HTTP response data string.
        """
        lines = []
        version = "HTTP/%d.%d" % response.version
        lines.append("%s %d %s" % (version, response.status, response.msg))
        lines.extend(response.headers)
        # an empty line ends the headers
        lines.extend(("", ""))
        data = "\r\n".join(lines)
        if response.content:
            data += response.content
        return data

    def parse_response_data (self, data):
        """
        Parse HTTP response data.
        @return: HTTP response
        @rtype: HttpResponse
        """
        # find status line
        i = data.find("\r\n")
        if i == -1:
            return None
        line, data = data.split("\r\n", 1)
        parts = line.split(None, 2)
        if len(parts) != 3:
            return None
        version, status, msg = parts
        # version has now format HTTP/x.y, convert to (x,y)
        version = (int(version[5]), int(version[7]))
        # status is an int
        status = int(status)
        headers = []
        i = data.find("\r\n\r\n")
        if i != -1:
            headerdata, data = data.split("\r\n\r\n", 1)
            fp = StringIO.StringIO(headerdata+"\r\n")
            rfcheaders = rfc822.Message(fp)
            fp.close()
            if "Transfer-Encoding" in rfcheaders:
                handler = TrailerHandler(headers)
                enctype = rfcheaders["Transfer-Encoding"]
                data = decode_transfer(enctype, data, handler)
                handler.handle_trailer()
            if "Content-Encoding" in rfcheaders:
                enctype = rfcheaders["Content-Encoding"]
                data = decode_content(enctype, data)
            # chop off the appending \r\n of each header
            headers.extend([x[:-2] for x in rfcheaders.headers])
        return HttpResponse(version, status, msg, headers, content=data)

    def check_response (self, response):
        """
        Check individual parts of the response with check_response_*
        methods.
        """
        self.assert_(response is not None)
        self.check_response_version(response)
        self.check_response_status(response)
        self.check_response_message(response)
        self.check_response_headers(response)
        self.check_response_content(response)

    def check_response_version (self, response):
        """
        Check HTTP response version.
        """
        self.assertEqual(response.version, self.get_response_version())

    def check_response_status (self, response):
        """
        Check HTTP response status.
        """
        self.assertEqual(response.status, self.get_response_status())

    def check_response_message (self, response):
        """
        Check HTTP response message.
        """
        # only check if status is what one expected
        if response.status == self.get_response_status():
            msg = self.get_response_message(response.status)
            self.assertEqual(response.msg, msg)

    def check_response_headers (self, response):
        """
        Check HTTP response headers.
        """
        # no standard checks here
        pass

    def check_response_content (self, response):
        """
        Check HTTP response content.
        """
        # only check if status is what one expected
        if response.status == self.get_response_status():
            self.assertEqual(response.content, self.get_response_content())

    def start_test (self):
        """
        Main test method. Start client and server, then send request
        and read response.
        """
        self.client = self.start_client()
        self.server = self.start_server()
        try:
            data = self.construct_request_data(self.get_request())
            self.client.connect(("", 8081))
            self.client.send_data(data)
            if wc.proxy.readable_socket(self.server.socket):
                self.server.handle_request()
            else:
                # the proxy answered already without connecting to the server
                pass
            data = self.client.read_data()
            response = self.parse_response_data(data)
            self.check_response(response)
        finally:
            self.server.server_close()
