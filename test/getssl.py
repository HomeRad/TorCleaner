#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""print headers of an url"""


def _main ():
    """USAGE: test/getssl.py <https url>"""
    import httplib, urlparse, sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    url = sys.argv[1]
    parts = urlparse.urlsplit(url)
    host = parts[1]
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection("localhost:8443")
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    print req.read()


if __name__=='__main__':
    _main()
