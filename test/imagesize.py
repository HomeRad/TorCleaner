#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Download one image and try to guess its size.
"""
import Image, sys
from StringIO import StringIO
from wc.update import open_url

def _main ():
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
