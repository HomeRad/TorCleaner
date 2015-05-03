#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Show previously generated profile data.
"""

import sys
import os
import wc

_profile = "webcleaner.prof"

def _main(filename):
    """
    Print profiling data and exit.
    """
    if not wc.HasPstats:
        print >> sys.stderr, "The `pstats' Python module is not installed."
        sys.exit(1)
    if not os.path.exists(filename):
        print >> sys.stderr, "Could not find file %r." % filename
        sys.exit(1)
    import pstats
    stats = pstats.Stats(filename)
    stats.strip_dirs().sort_stats("cumulative").print_stats(100)
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        _main(sys.argv[1])
    else:
        _main(_profile)
