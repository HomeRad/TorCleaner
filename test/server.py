#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""proxy server simulator"""

import sys
import wc
from wc.proxy import Listener, HttpClient, proxy_poll, run_timers


class TestClient (HttpClient.HttpClient):
    def server_request (self):
        assert self.state == 'receive'
        # XXX execute test
        print "huiiiii"


def main (port):
    Listener.Listener(port, TestClient)
    while True:
        proxy_poll(timeout=max(0, run_timers()))


if __name__=='__main__':
    wc.config = wc.Configuration()
    wc.config['filters'] = [] #['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    main(wc.config['port']+1)
