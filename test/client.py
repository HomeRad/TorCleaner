#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""client simulator"""

import sys, asyncore, socket
import wc
from wc.log import *
from wc.proxy import create_inet_socket

class ClientConnection (asyncore.dispatcher, object):

    def __init__(self, config, test):
        super(ClientConnection, self).__init__()
        create_inet_socket(self, socket.SOCK_STREAM)
        self.connect(('localhost', config['port']+1))
        self.outbuf, self.inbuf = get_data(config, test)


    def handle_connect (self):
        pass


    def handle_read (self):
        data = self.recv(8192)
        print "client got", `data`
        # XXX test data


    def handle_error (self):
        exception(PROXY, "%s error, closing", str(self))
        self.close()
        self.del_channel()


    def writable(self):
        return len(self.outbuf) > 0


    def handle_write (self):
        sent = self.send(self.outbuf)
        self.outbuf = self.outbuf[sent:]


    def handle_expt (self):
        exception(PROXY, "%s exception", str(self))


def get_data (config, test):
    im = "from test.tests.%s import client_send, client_recv" % test
    exec im
    return [ s%config for s in [client_send, client_recv] ]


def main (params):
    initlog("test/logging.conf")
    client = ClientConnection(wc.Configuration(), sys.argv[1])
    asyncore.loop()


if __name__=='__main__':
    main(sys.argv[1:])
