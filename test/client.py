#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""client simulator"""

import sys, asyncore, socket
import wc
from wc.log import *
from wc.proxy import create_inet_socket

class ClientConnection (asyncore.dispatcher, object):

    def __init__(self, config, data):
        super(ClientConnection, self).__init__()
        create_inet_socket(self, socket.SOCK_STREAM)
        self.connect(('localhost', config['port']))
        self.buf = data


    def handle_connect (self):
        pass


    def handle_read (self):
        data = self.recv(8192)
        # XXX test data


    def handle_error (self):
        exception(PROXY, "%s error, closing", str(self))
        self.close()
        self.del_channel()


    def writable(self):
        return len(self.buf) > 0


    def handle_write (self):
        sent = self.send(self.buf)
        self.buf = self.buf[sent:]


    def handle_expt (self):
        exception(PROXY, "%s exception", str(self))


def main (params):
    initlog("test/logging.conf")
    config = wc.Configuration()
    # XXX read data from file?
    data = "GET http://localhost:%(port)d/ HTTP/1.0\r\n\r\n" % config
    client = ClientConnection(config, data)
    asyncore.loop()


if __name__=='__main__':
    main(sys.argv[1:])
