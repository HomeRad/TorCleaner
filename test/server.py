#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""server simulator"""

import sys, os, logging


def get_data (config, test):
    exec "from test.tests.%s import server_send, server_recv"%test
    return [ s%config for s in [server_send, server_recv] ]


def startfunc ():
    from wc.proxy import Listener, proxy_poll, run_timers
    from test import TestClient
    Listener.Listener(wc.config['port'], TestClient)
    while True:
        proxy_poll(timeout=max(0, run_timers()))


def start (test):
    # init log
    logfile = os.path.join(os.getcwd(), "test", "logging.conf")
    initconsolelog(logfile)
    # init configuration
    import wc
    wc.config = wc.Configuration()
    # disable all filters
    wc.config['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
    # start one port above the proxy
    wc.config['port'] += 1
    pidfile = os.path.join(os.getcwd(), "test", "server.pid")
    msg, status = wc.daemon.start(startfunc, pidfile, parent_exit=False)


def _main ():
    command = sys.argv[1]
    if command=='start':
        start(sys.argv[2])
    elif command=='stop':
        from wc.daemon import stop
        msg, status = stop(pidfile)
    else:
        print "unknown command", `command`
    if msg:
        print >>sys.stderr, msg
    sys.exit(status)

if __name__=='__main__':
    #_main() # start the server process
    startfunc() # use this for testing
