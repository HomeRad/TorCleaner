#!/usr/bin/python
"""download one image and try to guess its size"""
import Image, sys
from StringIO import StringIO
try:
    from wc.update import open_url
except ImportError:
    print "using local development version"
    import os
    sys.path.insert(0, os.getcwd())
    from wc.update import open_url

def usage ():
    print "usage: imagesize.py <url> [bufsize]"
    sys.exit(1)

def test ():
    if len(sys.argv) < 2:
        usage()
    bufsize = 6000
    url = sys.argv[1]
    if len(sys.argv) > 3:
        bufsize = int(sys.argv[2])
    page = open_url(url)
    buf = StringIO()
    data = page.read()
    print "downloaded", len(data), "bytes"
    buf.write(data[:bufsize])
    buf.seek(0)
    dummy = Image.open(buf, 'r')


if __name__=='__main__':
    test()
