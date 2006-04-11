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
Test block filter.
"""

import sys
import os
import wc
import wc.http.header

def _main ():
    """
    USAGE: scripts/run.sh test/block.py <configdir> <url>
    """
    if len(sys.argv) != 3:
        print _main.__doc__.strip()
        sys.exit(1)
    confdir = sys.argv[1]
    url = sys.argv[2]
    data = "GET %s HTTP/1.0" % url
    logfile = os.path.join(confdir, "logging.conf")
    wc.initlog(logfile, filelogs=False)
    wc.configuration.config = wc.configuration.init(confdir=confdir)
    wc.configuration.config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    from wc.filter import applyfilter, get_filterattrs, STAGE_REQUEST
    headers = wc.http.header.WcMessage()
    headers['Content-Type'] = "text/html"
    attrs = get_filterattrs(url, [STAGE_REQUEST], headers=headers)
    print applyfilter(STAGE_REQUEST, data, 'finish', attrs)


if __name__ == '__main__':
    _main()
