#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""proxy client tester"""

import httplib, urlparse, sys
try:
    import wc
except ImportError:
    print "using local development version"
    import os
    sys.path.insert(0, os.getcwd())
    import wc

def main (tests):
    if not tests:
        tests.append('')
    for test in tests:
        _exec_test(test)


def exec_test (test):
    config = wc.Configuration()
    url = 'http://localhost:%d/%s' % (config['port']+1, test)
    h = httplib.HTTPConnection('localhost', config['port'])
    h.debug_level = 1
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", 'localhost')
    h.endheaders()
    req = h.getresponse()
    print req.msg


if __name__=='__main__':
    main(sys.argv[1:])
