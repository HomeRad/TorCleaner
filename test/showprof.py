#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

def _main (fname):
    import hotshot.stats
    stats = hotshot.stats.load(fname)
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(25)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        _main(sys.argv[1])
    else:
        _main("filter.prof")
