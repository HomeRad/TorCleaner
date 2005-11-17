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
Filter a given file in response modify stage.
"""

import sys
import os
import wc
import wc.configuration
import wc.filter
import wc.proxy
import wc.proxy.dns_lookups
import wc.http.header

profiling = False

extensions = {
    ".html": "text/html",
    ".xml": "text/xml",
    ".rss": "text/xml",
}

def get_content_type (filename, fp):
    default_type = "text/html"
    root, extension = os.path.splitext(filename)
    if extension in extensions:
        # found a known extension
        return extensions[extension]
    # use magic database
    import wc.magic
    content_type = wc.magic.classify(fp)
    if content_type:
        return content_type
    return default_type


def _main ():
    """
    USAGE: test/run.sh test/filterfile.py <config dir> <filename>
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
        logfile = os.path.join(confdir, "logging.conf")
        wc.initlog(logfile, wc.Name, filelogs=False)
        wc.configuration.config = wc.configuration.init(confdir=confdir)
        wc.configuration.config.init_filter_modules()
        wc.proxy.dns_lookups.init_resolver()
        headers = wc.http.header.WcMessage()
        content_type = get_content_type(fname, f)
        headers['Content-Type'] = content_type
        attrs = wc.filter.get_filterattrs(fname, "127.0.0.1",
                                      [wc.filter.STAGE_RESPONSE_MODIFY],
                                      headers=headers, serverheaders=headers)
        if profiling:
            import hotshot
            profile = hotshot.Profile("filter.prof")
            profile.runcall(_filter, f, attrs)
            profile.close()
            import hotshot.stats
            stats = hotshot.stats.load("filter.prof")
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats(25)
        else:
            _filter(f, attrs)
    finally:
        f.close()


def _filter (f, attrs):
    filtered = ""
    data = f.read(2048)
    while data:
        print >>sys.stderr, "Test: data", len(data)
        try:
            filtered += wc.filter.applyfilter(
                       wc.filter.STAGE_RESPONSE_MODIFY, data, 'filter', attrs)
        except wc.filter.FilterException, msg:
            print >>sys.stderr, "Test: exception:", msg
            pass
        data = f.read(2048)
    print >>sys.stderr, "Test: finishing"
    i = 1
    while True:
        print >>sys.stderr, "Test: finish", i
        try:
            filtered += wc.filter.applyfilter(
                         wc.filter.STAGE_RESPONSE_MODIFY, "", 'finish', attrs)
            break
        except wc.filter.FilterException, msg:
            print >>sys.stderr, "Test: finish: exception:", msg
            wc.proxy.proxy_poll(timeout=max(0, wc.proxy.run_timers()))
        i += 1
        if i==200:
            # background downloading if javascript is too slow
            print >>sys.stderr, "Test: oooooops"
            break
    print filtered,


if __name__ == '__main__':
    _main()
