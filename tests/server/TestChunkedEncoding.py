# -*- coding: iso-8859-1 -*-
"""base and utility classes for Proxy testing"""

import unittest
from tests.HttpServer import LogRequestHandler, random_chars
from tests.HttpRequest import HttpRequest
from tests.ProxyTest import ProxyTest


class ChunkRequestHandler (LogRequestHandler):

    body_length = 0x30

    def do_GET (self):
        """send chunk data"""
        body = random_chars(self.body_length)
        data = 'HTTP/1.1 200 OK\r\n'
        data += "Date: %s\r\n" % self.date_time_string()
        data += "Transfer-Encoding: chunked\r\n"
        data += "Connection: close\r\n"
        data += "\r\n"
        data += "0000000000%s\r\n" % hex(self.body_length)[2:]
        data += "%s\r\n" % body
        data += "0\r\n\r\n"
        self.server.log.write("server will send %d bytes\n" % len(data))
        self.print_lines(data)
        self.wfile.write(data)


class ChunkRequest (HttpRequest):
    def check_response (self, response):
        """check for 200 status and correct body data length"""
        if response.status!=200:
            return (self.VIOLATION, "Invalid HTTP status %r"%response.status)
        body = response.read()
        if len(body) != ChunkRequestHandler.body_length:
            return (self.VIOLATION,
             "Expected %d bytes in the body, but got %d bytes instead:\n%r" %\
             (ChunkRequestHandler.body_length, len(body), body))
        return (self.SUCCESS, "Ok")

    def name (self):
        return 'chunked-leading-zeros'


class TestChunkedEncoding (ProxyTest):
    def __init__ (self, methodName='runTest'):
        ProxyTest.__init__(self, methodName=methodName)
        request = ChunkRequest()
        self.addTest(request, handler_class=ChunkRequestHandler)


if __name__ == '__main__':
    unittest.main(defaultTest='TestChunkedEncoding')
else:
    suite = unittest.makeSuite(TestChunkedEncoding, 'test')

