#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""server simulator"""


def get_data (config, testklass):
    exec "from test.tests.%s import server_send, server_recv"%testklass
    return [ s%config for s in [server_send, server_recv] ]


def startfunc ():
    from wc.proxy import Listener, proxy_poll, run_timers
    from test import TestClient
    Listener.Listener(wc.config['port'], TestClient)
    while True:
        proxy_poll(timeout=max(0, run_timers()))


if __name__=='__main__':
    #_main() # start the server process
    startfunc() # use this for testing
