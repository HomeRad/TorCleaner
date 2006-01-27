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
Scan a given file with virus filter.
"""

import sys
import wc.filter.VirusFilter


def _main ():
    """
    USAGE: scripts/run.sh test/filtervirus.py <filename>
    """
    if len(sys.argv) != 2:
        print _main.__doc__.strip()
        sys.exit(1)
    fname = sys.argv[1]
    if fname == "-":
        f = sys.stdin
    else:
        f = file(fname)
    try:
        conf = wc.filter.VirusFilter.ClamavConfig("/etc/clamav/clamd.conf")
        scanner = wc.filter.VirusFilter.ClamdScanner(conf)
        data = f.read(1024)
        while data:
            scanner.scan(data)
            data = f.read(1024)
        scanner.close()
        print "File", repr(fname),
        print "infected", scanner.infected, "errors", scanner.errors
    finally:
        f.close()


if __name__ == '__main__':
    _main()
