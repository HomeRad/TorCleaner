#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""print headers of an url"""

import httplib, urlparse, sys, os

def request (url):
    parts = urlparse.urlsplit(url)
    host = parts[1]
    port = 8443
    if os.environ.get("WC_DEVELOPMENT", 0):
        port += 1
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection("localhost:%s"%port)
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    if req.status==302:
        url = req.msg.get('Location')
        print "redirected to", url
        return request(url)
    return req


def _main ():
    """USAGE: test/getssl.py <https url>"""
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    req = request(sys.argv[1])
    print "HTTP version", req.version, req.status, req.reason
    print req.msg
    print req.read()


if __name__=='__main__':
    _main()
