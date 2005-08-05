#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
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
import wc.proxy.Headers

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
    """USAGE: test/run.sh test/filterfile.py <config dir> <filename>"""
    if len(sys.argv)!=3:
        print _main.__doc__
        sys.exit(1)
    confdir = sys.argv[1]
    fname = sys.argv[2]
    if fname == "-":
        f = sys.stdin
    else:
        f = file(fname)
    logfile = os.path.join(confdir, "logging.conf")
    wc.initlog(logfile, wc.Name, filelogs=False)
    wc.configuration.config = wc.configuration.init(confdir=confdir)
    wc.configuration.config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    headers = wc.proxy.Headers.WcMessage()
    content_type = get_content_type(fname, f)
    headers['Content-Type'] = content_type
    attrs = wc.filter.get_filterattrs(fname, "127.0.0.1",
                                      [wc.filter.STAGE_RESPONSE_MODIFY],
                                      headers=headers, serverheaders=headers)
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
    print "Filtered:", filtered


if __name__=='__main__':
    _main()
