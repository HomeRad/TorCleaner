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

from cStringIO import StringIO
import rfc822
import unittest
import socket
import select
import BaseHTTPServer


###################### utility functions ######################

def readable (sock):
    """
    Check if socket is readable.
    """
    try:
        r, w, e = select.select([sock], [], [], 0.5)
        return (sock in r)
    except select.error:
        return False


def decode (encoding, data):
    """
    Decode data with given content-encoding.
    """
    if encoding == "gzip":
        import gzip
        buf = StringIO(data)
        fp = gzip.GzipFile("", "rb", 9, buf)
        data = fp.read()
        fp.close()
        buf.close()
    elif encoding == "compress":
        import zlib
        data = zlib.decompress(data)
    elif encoding == "identity":
        pass
    return data


class HttpData (object):
    """
    Store HTTP data.
    """

    def __init__ (self, headers, content=None):
        self.headers = headers
        self.content = content

    def has_header (self, name):
        """
        Test if header with given name is stored.
        """
        # HTTP headers are case insensitive
        key = name.lower()
        for header in self.headers:
            if header.lower().startswith("%s:" % key):
                return True
        return False

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
        raise KeyError, name


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

    def connect (self, addr):
        self.socket = socket.socket()
        self.socket.connect(addr)

    def send_data (self, data):
        """
        Send complete data to socket.
        """
        self.socket.sendall(data)

    def read_data (self):
        """
        Read until no more data is available.
        """
        data = ""
        while readable(self.socket):
            s = self.socket.recv(4096)
            if not s:
                break
            data += s
        return data


class HttpRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Custom HTTP request handler.
    """

    def handle_one_request (self):
        """
        Read one request and parse it. Then let the TestCase class
        check the request and construct the response which is sent back.
        """
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

    def log_request (self, code='-', size='-'):
        """
        Suppress request logging.
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
            content = self.rfile.read(clen)
        else:
            content = ""
        return HttpRequest(method, uri, version, headers, content=content)



################ Proxy tests ######################

class ProxyTest (unittest.TestCase):

    # the proxy to test must be started
    needed_resources = ['proxy']

    def setUp (self):
        super(ProxyTest, self).setUp()
        self.check_resources(self.needed_resources)

    def start_client (self):
        """
        Start a HTTP client which is ready for use.
        @return: http client
        @rtype: HttpClient
        """
        client = HttpClient()
        client.connect(("", 8081))
        return client

    def start_server (self):
        """
        Start a HTTP server which is ready for use.
        @return: http server
        @rtype: BaseHTTPServer.HTTPServer
        """
        port = 8000
        server_address = ('', port)
        HandlerClass = HttpRequestHandler
        HandlerClass.protocol_version = "HTTP/1.1"
        ServerClass = BaseHTTPServer.HTTPServer
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
        return "GET"

    def get_request_uri (self):
        return "/"

    def get_request_version (self):
        return (1, 1)

    def get_request_content (self):
        return ""

    def get_request_headers (self, content):
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
        self.assertEquals(request.method, self.get_request_method())

    def check_request_uri (self, request):
        self.assertEquals(request.uri, self.get_request_uri())

    def check_request_version (self, request):
        self.assertEquals(request.version, self.get_request_version())

    def check_request_headers (self, request):
        pass

    def check_request_content (self, request):
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
        return (1, 1)

    def get_response_status (self):
        return 200

    def get_response_message (self, status):
        return "Ok"

    def get_response_content (self):
        return "hui"

    def get_response_headers (self, content):
        return [
            "Content-Type: text/plain",
            "Content-Length: %d" % len(content),
        ]

    def construct_response_data (self, response):
        """
        Construct valid HTTP response data string.
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
            fp = StringIO(headerdata+"\r\n")
            rfcheaders = rfc822.Message(fp)
            fp.close()
            if "Content-Encoding" in rfcheaders:
                data = decode(rfcheaders["Content-Encoding"], data)
            # chop off the appending \r\n of each header
            headers = list([x[:-2] for x in rfcheaders.headers])
        else:
            headers = []
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
        self.assertEqual(response.version, self.get_response_version())

    def check_response_status (self, response):
        self.assertEqual(response.status, self.get_response_status())

    def check_response_message (self, response):
        msg = self.get_response_message(response.status)
        self.assertEqual(response.msg, msg)

    def check_response_headers (self, response):
        pass

    def check_response_content (self, response):
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
            self.client.send_data(data)
            if readable(self.server.socket):
                self.server.handle_request()
            else:
                # the proxy answered already without connecting to the server
                pass
            data = self.client.read_data()
            response = self.parse_response_data(data)
            self.check_response(response)
        finally:
            self.server.server_close()


def make_suite (prefix, namespace):
    """
    Add all ProxyTest classes starting with given prefix to a test suite.

    @return: test suite
    @rtype: unittest.TestSuite
    """
    classes = [value for key, value in namespace.items() \
               if key.startswith(prefix) and issubclass(value, ProxyTest)]
    loader = unittest.defaultTestLoader
    tests = [loader.loadTestsFromTestCase(clazz) for clazz in classes]
    return unittest.TestSuite(tests)
