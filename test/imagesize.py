#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Download one image and try to guess its size.
"""
import Image, sys
from StringIO import StringIO
from wc.update import open_url

def _main():
    """"
    USAGE: scripts/run.sh test/imagesize.py <url> [bufsize]
    """
    if len(sys.argv) != 2:
        print _main.__doc__.strip()
        sys.exit(1)
    bufsize = 6000
    url = sys.argv[1]
    if len(sys.argv) > 2:
        bufsize = int(sys.argv[2])
    print "using bufsize", bufsize
    page = open_url(url)
    data = page.read()
    print "downloaded", len(data), "bytes"
    buf = StringIO()
    pos = 0
    while True:
        buf.write(data[pos:bufsize])
        pos = bufsize
        buf.seek(0)
        try:
            dummy = Image.open(buf, 'r')
            print "succeeded at bufsize", bufsize
            break
        except IOError:
            buf.seek(bufsize)
            bufsize += 2000
            print "increased buf to", bufsize
    assert data.startswith(buf.getvalue())


if __name__ == '__main__':
    _main()
