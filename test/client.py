#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""client simulator"""

import asyncore, socket
import wc
from wc.log import *
from wc.proxy import create_inet_socket

class ClientConnection (asyncore.dispatcher, object):

    def __init__(self, config, test):
        super(ClientConnection, self).__init__()
        create_inet_socket(self, socket.SOCK_STREAM)
        self.connect(('localhost', config['port']+1))
        self.outbuf = get_data(config, test)


    def handle_connect (self):
        pass


    def handle_read (self):
        data = self.recv(8192)
        # XXX


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
    exec "from test.tests.%s import client_send" % test
    client_send%config


def _main (params):
    """USAGE: XXX"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    initlog("test/logging.conf")
    client = ClientConnection(wc.Configuration(), sys.argv[1])
    asyncore.loop()


if __name__=='__main__':
    _main()
