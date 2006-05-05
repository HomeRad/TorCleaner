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
Test image reduction filter.
"""

import sys
import os
import stat
import mimetypes
import cStringIO as StringIO
import wc
import wc.http.header

def _main ():
    """
    USAGE: test/run.sh test/imagereduce.py <confdir> <img-file> > reduced.jpg
    """
    if len(sys.argv) != 3:
        print _main.__doc__.strip()
        sys.exit(1)
    confdir = sys.argv[1]
    fname = sys.argv[2]
    if fname == "-":
        f = sys.stdin
    else:
        f = file(fname)
    try:
        data = f.read()
    finally:
        f.close()
    logfile = os.path.join(confdir, "logging.conf")
    wc.initlog(logfile, filelogs=False)
    config = wc.configuration.init(confdir=confdir)
    config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    headers = wc.http.header.WcMessage(StringIO(''))
    headers['Content-Type'] = mimetypes.guess_type(f)[0]
    headers['Content-Size'] = os.stat(f)[stat.ST_SIZE]
    from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY
    attrs = get_filterattrs(f, [STAGE_RESPONSE_MODIFY], headers=headers)
    filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)
    print filtered,


if __name__ == '__main__':
    _main()
