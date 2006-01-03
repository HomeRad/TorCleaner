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

def _main (args):
    """
    USAGE: test/run.sh test/parsefile.py test.html.
    """
    if len(args) < 1:
        print _main.__doc__.strip()
        sys.exit(1)
    from wc.HtmlParser.htmllib import HtmlPrinter, HtmlPrettyPrinter
    if args[0] == "-p":
        klass = HtmlPrettyPrinter
        filename = args[1]
    else:
        klass = HtmlPrinter
        filename = args[0]
    if filename == '-':
        f = sys.stdin
    else:
        f = open(filename)
    from wc.HtmlParser import htmlsax
    p = htmlsax.parser(klass())
    p.debug(1)
    size = 1024
    #size = 1 # feed data to parser one character-at-a-time
    data = f.read(size)
    while data:
        p.feed(data)
        data = f.read(size)
    p.flush()

if __name__ == '__main__':
    import sys
    _main(sys.argv[1:])
