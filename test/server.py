#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""server simulator"""

import sys, os
import wc
# init configuration before anything else
wc.config = wc.Configuration()
# disable all filters
wc.config['filterlist'] = [[],[],[],[],[],[],[],[],[],[]]
wc.config['port'] += 1
from wc.log import *
from wc.proxy import HttpClient


class TestClient (HttpClient.HttpClient):
    """client reading requests and echoing back a predefined answer"""
    def server_request (self):
        assert self.state == 'receive'
        # XXX execute test
        print "huiiiii"


def get_data (config, test):
    im = "from test.tests.%s import server_send, server_recv" % test
    exec im
    return [ s%config for s in [server_send, server_recv] ]


def startfunc ():
    initlog(logfile)
    from wc.proxy import Listener, proxy_poll, run_timers
    Listener.Listener(wc.config['port'], TestClient)
    while True:
        proxy_poll(timeout=max(0, run_timers()))


def main ():
    global test
    command = sys.argv[1]
    pidfile = os.path.join(os.getcwd(), "test", "server.pid")
    if command=='start':
        from wc.daemon import start
        test = sys.argv[2]
        msg, status = start(startfunc, pidfile, parent_exit=False)
    elif command=='stop':
        from wc.daemon import stop
        msg, status = stop(pidfile)
    else:
        print "unknown command", `command`
    if msg:
        print >>sys.stderr, msg
    sys.exit(status)

if __name__=='__main__':
    global logfile
    logfile = os.path.join(os.getcwd(), "test", "logging.conf")
    #main() # start the server process
    startfunc() # use this for testing
