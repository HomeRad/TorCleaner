#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test image reduction filter.
"""

import sys
import os
import stat
import mimetypes
import cStringIO as StringIO
import wc.http.header

def _main():
    """
    USAGE: scripts/run.sh test/imagereduce.py <confdir> <img-file> > reduced.jpg
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
