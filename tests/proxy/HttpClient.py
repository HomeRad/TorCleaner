import socket
import httplib
import wc.proxy.Dispatcher

class LogHttpClient (object):
    def __init__ (self, log, proxyconfig):
        self.log = log
        self.proxyconfig = proxyconfig
        self.addr = (socket.gethostbyname('localhost'), self.proxyconfig['port'])
        self.debug = 0

    def doRequest (self, request):
        self.sock = self.create_socket(self.addr)
        self.send(request.get_request())


    def send (self, data):
        self.log.write("client will send %d bytes to %s:\n" % (len(data), str(self.addr)))
        self.print_lines(data)
        self.sock.sendall(data)

    def recv (self):
        data = ''
        while True:
            d = self.sock.recv(4096)
            if d:
                data += d
            else:
                break
        self.log.write("client received %d bytes from %s:\n" % (len(data), str(self.addr)))
        self.print_lines(data)
        return data

    def print_lines (self, data):
        self.log.write("\n")
        for line in data.splitlines(True):
            self.log.write("  %r\n" % line)
        self.log.write("\n")

    def create_socket (self, addr, sslctx=None):
        self.log.write("connecting to %s\n"%str(addr))
        sock = wc.proxy.Dispatcher.create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=sslctx)
        sock.connect(addr)
        return sock

    def doResponse (self):
        self.response = httplib.HTTPResponse(self.sock)
        self.response.begin()

