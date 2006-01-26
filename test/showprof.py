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
Show previously generated profile data.
"""

import sys
import os
import wc

_profile = "webcleaner.prof"

def _main (filename):
    """
    Print profiling data and exit.
    """
    if not wc.HasPstats:
        print >> sys.stderr, "The `pstats' Python module is not installed."
        sys.exit(1)
    if not os.path.isfile(filename):
        print >> sys.stderr, "Could not find regular file %r." % filename
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
