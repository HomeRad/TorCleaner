import tests.proxy.HttpServer

class HttpRequest (object):
    SUCCESS = 0
    VIOLATION = 1
    FAILURE = 2

    def __init__ (self, serverconfig=tests.proxy.HttpServer.defaultconfig):
        self.serverconfig = serverconfig
        self.url = None


    def name (self):
        return self.__class__.__name__

    def get_request (self):
        """return string of complete request data (with headers and body)"""
        line = self.get_request_line()
        headers = self.get_request_headers()
        body = self.get_request_body()
        return "%s\r\n%s\r\n%s" % (line, headers, body)

    def get_request_line (self):
        """return request line, usually of the form
           *<scheme> <path> <httpver>*
        """
        rand = tests.proxy.HttpServer.random_chars(10)
        host = self.serverconfig['host']
        port = self.serverconfig['port']
        self.url = "http://%s:%d/%s" % (host, port, rand)
        return "GET %s HTTP/1.1" % self.url

    def get_request_headers (self):
        host = self.serverconfig['host']
        port = self.serverconfig['port']
        return "Host: %s:%d\r\nProxy-Connection: close\r\n" % (host, port)

    def get_request_body (self):
        return ""

    def check_response (self, response):
        """Look if response has expected data. Result can be

             - SUCCESS - everything went as expected
             - VIOLATION - received data was not what has been expected
             - FAILURE - an error occured during the test execution

           The result message has detailed information about the result.

           return tuple `(result, msg)`"""
        raise NotImplementedError, "must be overridden in subclass"

