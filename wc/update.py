# -*- coding: iso-8859-1 -*-
"""routines for updating filter and rating configuration"""

import os
import md5
import wc
from wc.filter.Rating import rating_cache_merge, rating_cache_parse

#
# urlutils.py - Simplified urllib handling
#
#   Written by Chris Lawrence <lawrencc@debian.org>
#   (C) 1999-2002 Chris Lawrence
#
# This program is freely distributable per the following license:
#
##  Permission to use, copy, modify, and distribute this software and its
##  documentation for any purpose and without fee is hereby granted,
##  provided that the above copyright notice appears in all copies and that
##  both that copyright notice and this permission notice appear in
##  supporting documentation.
##
##  I DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL
##  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL I
##  BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
##  DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
##  WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
##  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
##  SOFTWARE.
#
# Version 2.19; see changelog for revision history
#
# modified by Bastian Kleineidam <calvin@users.sf.net> for WebCleaner

import httplib
import urllib
import urllib2
import re
import socket
import zlib
import gzip
import cStringIO as StringIO

UA_STR = '%s/%s' % (wc.Name, wc.Version)

def decode (page):
    "gunzip or deflate a compressed page"
    encoding = page.info().get("Content-Encoding") 
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        # cannot seek in socket descriptors, so must get content now
        content = page.read()
        if encoding == 'deflate':
            fp = StringIO.StringIO(zlib.decompress(content))
        else:
            fp = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(content))
        # remove content-encoding header
        headers = {}
        ceheader = re.compile(r"(?i)content-encoding:")
        for h in page.info().keys():
            if not ceheader.match(h):
                headers[h] = page.info()[h]
        page = urllib.addinfourl(fp, headers, page.geturl())
    return page


class HttpWithGzipHandler (urllib2.HTTPHandler):
    "support gzip encoding"
    def http_open (self, req):
        return decode(urllib2.HTTPHandler.http_open(self, req))


if hasattr(httplib, 'HTTPS'):
    class HttpsWithGzipHandler (urllib2.HTTPSHandler):
        "support gzip encoding"
        def http_open (self, req):
            """open gzip-decoded request with https handler"""
            return decode(urllib2.HTTPSHandler.http_open(self, req))


_opener = None
def urlopen (url, proxies=None, data=None):
    """Return connected request object for given url.
       All errors raise exceptions."""
    global _opener
    if proxies is None:
        proxies = urllib.getproxies()
    headers = {'User-Agent': UA_STR,
               'Accept-Encoding' : 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5'}
    request = urllib2.Request(url, data, headers)
    proxy_support = urllib2.ProxyHandler(proxies)
    if _opener is None:
        handlers = [proxy_support,
            urllib2.UnknownHandler, HttpWithGzipHandler,
            urllib2.ProxyBasicAuthHandler, urllib2.ProxyDigestAuthHandler,
            urllib2.HTTPDefaultErrorHandler, urllib2.HTTPRedirectHandler,
        ]
        if hasattr(httplib, 'HTTPS'):
            handlers.append(HttpsWithGzipHandler)
        _opener = urllib2.build_opener(*handlers)
        # print _opener.handlers
        urllib2.install_opener(_opener)
    return _opener.open(request)


# Global useful URL opener; throws IOError on error
def open_url (url, proxies=None):
    """return connected request object for given url.
       Raises IOError on error"""
    try:
        page = urlopen(url, proxies=proxies)
    except urllib2.HTTPError, x:
        wc.log.error(wc.LOG_GUI, "could not open url %r", url)
        raise IOError, x
    except (socket.gaierror, socket.error, urllib2.URLError), x:
        wc.log.error(wc.LOG_GUI, "could not open url %r", url)
        raise IOError, "no network access available"
    except IOError, data:
        wc.log.error(wc.LOG_GUI, "could not open url %r", url)
        if data and data[0] == 'http error' and data[1] == 404:
            raise IOError, data
        else:
            raise IOError, "no network access available"
    except OSError, data:
        raise IOError, data
    return page


# ====================== end of urlutils.py =================================

def update_filter (wconfig, dryrun=False, log=None):
    """Update the given configuration object with .zap files found at baseurl.
    If dryrun is True, only print out the changes but do nothing
    throws IOError on error
    """
    chg = False
    baseurl = wconfig['baseurl']+"filter/"
    url = baseurl+"filter-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >>log, "error fetching %s:"%url, msg
        return chg
    # remember all local config files
    filemap = {}
    for filename in wc.filterconf_files(wconfig.filterdir):
        filemap[os.path.basename(filename)] = filename
    # read md5sums
    for line in page.read().splitlines():
        if "<" in line:
            print >>log, "error fetching", url
            return chg
        if not line:
            continue
        md5sum, filename = line.split()
        assert filename.endswith('.zap')
        fullname = os.path.join(wc.ConfigDir, filename)
        # compare checksums
        if filemap.has_key(filename):
            f = file(fullname)
            data = f.read()
            digest = list(md5.new(data).digest())
            f.close()
            digest = "".join([ "%0.2x"%ord(c) for c in digest ])
            if digest==md5sum:
                print >>log, wc.i18n._("filter %s not changed, ignoring")%filename
                continue
            print >>log, wc.i18n._("updating filter %s")%filename
        else:
            print >>log, wc.i18n._("adding new filter %s")%filename
        # parse new filter
        url = baseurl+filename
        page = open_url(url)
        p = wc.ZapperParser(fullname, wconfig, compile_data=False)
        p.parse(fp=page)
        page.close()
        if wconfig.merge_folder(p.folder, dryrun=dryrun, log=log):
            chg = True

    url = baseurl+"extern-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >>log, wc.i18n._("error fetching %s:")%url, msg
        return chg
    lines = page.read().splitlines()
    page.close()
    for line in lines:
        if "<" in line:
            print >>log, wc.i18n._("error fetching %s:")%url, wc.i18n._("invalid content")
            return chg
        if not line:
            continue
        md5sum, filename = line.split()
        # XXX UNIX-generated md5sum filenames with subdirs are not portable
        fullname = os.path.join(wc.ConfigDir, filename)
        # compare checksums
        if os.path.exists(fullname):
            f = file(fullname)
            data = f.read()
            digest = list(md5.new(data).digest())
            f.close()
            digest = "".join([ "%0.2x"%ord(c) for c in digest ])
            if digest==md5sum:
                print >>log, wc.i18n._("extern filter %s not changed, ignoring")%filename
                continue
            print >>log, wc.i18n._("updating extern filter %s")%filename
        else:
            print >>log, wc.i18n._("adding new extern filter %s")%filename
        chg = True
        if not dryrun:
            url = baseurl+filename
            try:
                page = open_url(url)
            except IOError, msg:
                print >>log, wc.i18n._("error fetching %s:")%url, msg
                continue
            data = page.read()
            if not data:
                print >>log, wc.i18n._("error fetching %s:")%url, \
                             wc.i18n._("got no data")
                continue
            f = file(fullname, 'wb')
            f.write(data)
            f.close()
    return chg


def update_ratings (wconfig, dryrun=False, log=None):
    """update rating database from configured online rating service"""
    chg = False
    baseurl = wconfig['baseurl']+"rating/"
    url = baseurl+"rating.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >>log, "error fetching %s:"%url, msg
        return chg
    # build local rating cache, and merge
    chg = rating_cache_merge(rating_cache_parse(page), dryrun=dryrun, log=log)
    return chg
