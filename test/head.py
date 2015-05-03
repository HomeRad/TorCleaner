#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Print headers of an URL.
"""


def _main():
    """
    USAGE: scripts/run.sh test/head.py <url>
    """
    import httplib, urlparse, sys
    if len(sys.argv) != 2:
        print _main.__doc__.strip()
        sys.exit(1)
    url = sys.argv[1]
    parts = urlparse.urlsplit(url)
    host = parts[1]
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPConnection(host)
    h.connect()
    # skip_accept_encoding=1
    h.putrequest("HEAD", path, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    print req.msg


if __name__ == '__main__':
    _main()
