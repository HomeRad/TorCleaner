#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""server simulator"""

import sys
import wc
from wc.log import *
from wc.proxy import HttpClient


class TestClient (HttpClient.HttpClient):
    def server_request (self):
        assert self.state == 'receive'
        # XXX execute test
        print "huiiiii"


def get_data (config, test):
    im = "from test.tests.%s import server_send, server_recv" % test
    exec im
    return [ s%config for s in [server_send, server_recv] ]


def main ():
    initlog("test/logging.conf")
    wc.config = wc.Configuration()
    # disable all filters
    wc.config['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
    port = wc.config['port']+1
    from wc.proxy import Listener, proxy_poll, run_timers
    Listener.Listener(port, TestClient)
    while True:
        proxy_poll(timeout=max(0, run_timers()))


if __name__=='__main__':
    main()
