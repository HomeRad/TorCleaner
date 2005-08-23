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
USAGE: test/run.sh test/pfilterfile.py <.html file>
"""

import sys
import wc
import wc.filter

if len(sys.argv)!=2:
    print __doc__
    sys.exit(1)
f = sys.argv[1]
data = file(f).read()
from test import initlog
initlog("test/logging.conf")
wc.configuration.config = wc.configuration.init()
wc.configuration.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
wc.configuration.config.init_filter_modules()
attrs = wc.filter.get_filterattrs(f, [wc.filter.FILTER_RESPONSE_MODIFY])

def _main ():
    import hotshot
    profile = hotshot.Profile("filter.prof")
    profile.run("wc.filter.applyfilter(wc.filter.FILTER_RESPONSE_MODIFY, "+
                "data, 'finish', attrs)")
    profile.close()

if __name__=='__main__':
    _main()
