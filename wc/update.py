# -*- coding: iso-8859-1 -*-
import os, md5, wc
from wc.log import *

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

import httplib, urllib, urllib2, re, socket
UA_STR = '%s/%s' % (wc.Name, wc.Version)

def decode (page):
    "gunzip or deflate a compressed page"
    encoding = page.info().get("Content-Encoding") 
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        from cStringIO import StringIO
        # cannot seek in socket descriptors, so must get content now
        content = page.read()
        if encoding == 'deflate':
            import zlib
            fp = StringIO(zlib.decompress(content))
        else:
            import gzip
            fp = gzip.GzipFile('', 'rb', 9, StringIO(content))
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
            return decode(urllib2.HTTPSHandler.http_open(self, req))


_opener = None
def urlopen (url, proxies=None, data=None):
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
    try:
        page = urlopen(url, proxies=proxies)
    except urllib2.HTTPError, x:
        error(GUI, "could not open url %r", url)
        raise IOError, x
    except (socket.gaierror, socket.error, urllib2.URLError), x:
        error(GUI, "could not open url %r", url)
        raise IOError, "no network access available"
    except IOError, data:
        error(GUI, "could not open url %r", url)
        if data and data[0] == 'http error' and data[1] == 404:
            raise IOError, data
        else:
            raise IOError, "no network access available"
    return page


# ====================== end of urlutils.py =================================

def update (wconfig, baseurl, dryrun=False, log=None):
    """Update the given configuration object with .zap files found at baseurl.
    If dryrun is True, only print out the changes but do nothing
    throws IOError on error
    """
    chg = False
    url = baseurl+"filter-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >>log, "error fetching %s:"%url, msg
        return chg
    # remember all local config files
    filemap = {}
    for filename in wc.filterconf_files():
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
                print >>log, "filter", filename, "not changed, ignoring"
                continue
            print >>log, "updating filter", filename
        else:
            print >>log, "adding new filter", filename
        # parse new filter
        url = baseurl+filename+".gz"
        page = open_url(url)
        p = wc.ZapperParser(fullname, compile_data=False)
        p.parse(page, wconfig)
        chg = wconfig.merge_folder(p.folder, dryrun=dryrun, log=log) or chg

    url = baseurl+"extern-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >>log, "error fetching %s:"%url, msg
        return chg
    for line in page.read().splitlines():
        if "<" in line:
            print >>log, "error fetching", url
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
                print >>log, "extern filter", filename, "not changed, ignoring"
                continue
            print >>log, "updating extern filter", filename
        else:
            print >>log, "adding new extern filter", filename
        chg = True
        if not dryrun:
            url = baseurl+filename
            try:
                page = open_url(url)
            except IOError, msg:
                print >>log, "error fetching", url
                continue
            data = page.read()
            if not data:
                print >>log, "got no data from", url
                continue
            f = file(fullname, 'wb')
            f.write(data)
            f.close()
    return chg


def _test ():
    # test base url for all files
    initlog("test/logging.conf")
    baseurl = "http://localhost/~calvin/webcleaner.sf.net/htdocs/test/"
    update(wc.Configuration(), baseurl, dryrun=True)


if __name__=='__main__':
    _test()

