import threading
import random
import string
import time
import socket
import BaseHTTPServer

_lock = None
_server = None

def _acquireLock ():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    global _lock
    if not _lock:
        _lock = threading.RLock()
    if _lock:
        _lock.acquire()

def _releaseLock ():
    """Release the module-level lock acquired by calling _acquireLock()."""
    if _lock:
        _lock.release()


class LogHttpServer (BaseHTTPServer.HTTPServer):

    def __init__ (self, address, handler, log):
        BaseHTTPServer.HTTPServer.__init__(self, address, handler)
        self.abort = False
        self.log = log
        self.socket.setblocking(0)
        self.log.write("server %s accepting HTTP queries at %s with %s\n" % \
        (self.__class__.__name__, str(self.server_address), handler.__name__))

    def serve_until_stopped (self):
        """Handle one request at a time until doomsday."""
        abort = False
        while not abort:
            try:
                self.handle_request()
            except socket.error:
                time.sleep(1)
            _acquireLock()
            abort = self.abort
            _releaseLock()
        self.server_close()
        self.log.write("server %s closed\n" % str(self.server_address))



def random_chars (size):
    lmax = len(string.ascii_lowercase)
    s = []
    while size > lmax:
        s.extend(random.sample(string.ascii_lowercase, lmax))
        size -= lmax
    s.extend(random.sample(string.ascii_lowercase, size))
    return "".join(s)


class LogRequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message (self, format, *args):
        # shut up
        pass

    def parse_request (self):
        res = BaseHTTPServer.BaseHTTPRequestHandler.parse_request(self)
        if res:
            self.server.log.write("server got request\n")
            self.server.log.write("\n")
            self.server.log.write("  %r\n" % (self.requestline+"\r\n"))
            for line in self.headers.headers:
                self.server.log.write("  %r\n" % line)
        else:
            self.server.log.write("server got invalid request\n")
            self.server.log.write("  %r\n" % (self.requestline+"\r\n"))
        self.server.log.write("\n")
        return res

    def do_GET (self):
        body = "body-%s"%random_chars(10)
        data = 'HTTP/1.1 200 OK\r\n'
        data += "Content-Length: %d\r\n" % len(body)
        data += "Connection: close\r\n"
        data += "\r\n"
        data += body
        self.server.log.write("server will send %d bytes\n" % len(data))
        self.print_lines(data)
        self.wfile.write(data)

    def print_lines (self, data):
        self.server.log.write("\n")
        for line in data.splitlines(True):
            self.server.log.write("  %r\n" % line)
        self.server.log.write("\n")


def runServer (server_class, handler_class, port, log):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class, log)
    global _server
    _acquireLock()
    _server = httpd
    _releaseLock()
    httpd.serve_until_stopped()


# default test server runs on localhost:8000
defaultconfig = {
  'host': 'localhost',
  'port': 8000,
}


def startServer (log, server_class=LogHttpServer,
                 handler_class=LogRequestHandler, port=defaultconfig['port']):
    t = threading.Thread(target=runServer,
                         args=(server_class, handler_class, port, log))
    t.start()
    # wait until server is started
    global _server
    running = False
    while not running:
        _acquireLock()
        running = _server is not None
        _releaseLock()
    time.sleep(2)
    return t


def stopServer (log):
    log.write("About to stop server...\n")
    global _server
    _acquireLock()
    _server.abort = True
    _releaseLock()
    time.sleep(2)

