#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Scan a given file with virus filter.
"""

import sys
import wc.filter.VirusFilter


def _main():
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
