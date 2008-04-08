# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2008 Bastian Kleineidam
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
Routines for updating filter and rating configuration.
"""

import os
import md5

import wc
import log
import configuration
#XXXfrom filter.Rating import rating_cache_merge, rating_cache_parse

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
import cStringIO as StringIO
from wc import gzip2 as gzip

UA_STR = '%s/%s' % (wc.Name, wc.Version)

def decode (page):
    """
    Gunzip or deflate a compressed page.
    """
    encoding = page.info().get("Content-Encoding")
    # note: some servers send content encoding gzip if file ends with ".gz"
    # but we don't want to decompress such files
    if encoding in ('gzip', 'x-gzip', 'deflate') and \
       not page.geturl().endswith(".gz"):
        # cannot seek in socket descriptors, so must get content now
        content = page.read()
        if encoding == 'deflate':
            fp = StringIO.StringIO(zlib.decompress(content))
        else:
            fp = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(content))
        # remove content-encoding header
        headers = {}
        ceheader = re.compile(r"(?i)content-encoding:")
        for h in page.info().iterkeys():
            if not ceheader.match(h):
                headers[h] = page.info()[h]
        newpage = urllib.addinfourl(fp, headers, page.geturl())
        if hasattr(page, "code"):
            # python 2.4 compatibility
            newpage.code = page.code
        if hasattr(page, "msg"):
            # python 2.4 compatibility
            newpage.msg = page.msg
        page = newpage
    return page


class HttpWithGzipHandler (urllib2.HTTPHandler):
    """
    Support gzip encoding.
    """

    def http_open (self, req):
        """
        Open and gunzip request data.
        """
        return decode(urllib2.HTTPHandler.http_open(self, req))


if hasattr(httplib, 'HTTPS'):
    class HttpsWithGzipHandler (urllib2.HTTPSHandler):
        """
        Support gzip encoding.
        """

        def http_open (self, req):
            """
            Open and gunzip request data.
            """
            return decode(urllib2.HTTPSHandler.http_open(self, req))


class PasswordManager (object):
    """
    Simple user/password store.
    """

    def __init__ (self, user, password):
        """
        Store given credentials.
        """
        self.user = user
        self.password = password

    def add_password (self, realm, uri, user, passwd):
        """
        Already have the password, ignore parameters.
        """
        pass

    def find_user_password (self, realm, authuri):
        """
        Return stored credentials.
        """
        return self.user, self.password


_opener = None
def urlopen (url, proxies=None, data=None):
    """
    Return connected request object for given url.
    All errors raise exceptions.
    """
    global _opener
    if proxies is None:
        proxies = urllib.getproxies()
    headers = {
       'User-Agent': UA_STR,
       'Accept-Encoding' : 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5',
    }
    request = urllib2.Request(url, data, headers)
    proxy_support = urllib2.ProxyHandler(proxies)
    if _opener is None:
        # XXX heh, not really protected :)
        pwd_manager = PasswordManager("WebCleaner", "imadoofus")
        handlers = [proxy_support,
            urllib2.UnknownHandler,
            HttpWithGzipHandler,
            urllib2.HTTPBasicAuthHandler(pwd_manager),
            urllib2.ProxyBasicAuthHandler(pwd_manager),
            urllib2.HTTPDigestAuthHandler(pwd_manager),
            urllib2.ProxyDigestAuthHandler(pwd_manager),
            urllib2.HTTPDefaultErrorHandler,
            urllib2.HTTPRedirectHandler,
        ]
        if hasattr(httplib, 'HTTPS'):
            handlers.append(HttpsWithGzipHandler)
        _opener = urllib2.build_opener(*handlers)
        # print _opener.handlers
        urllib2.install_opener(_opener)
    return _opener.open(request)


# Global useful URL opener; throws IOError on error
def open_url (url, proxies=None):
    """
    Return connected request object for given url.

    @raise: IOError
    """
    try:
        page = urlopen(url, proxies=proxies)
    except urllib2.HTTPError, x:
        log.error(wc.LOG_GUI, "could not open url %r", url)
        raise IOError(x)
    except (socket.gaierror, socket.error, urllib2.URLError), x:
        log.error(wc.LOG_GUI, "could not open url %r", url)
        raise IOError("no network access available")
    except IOError, data:
        log.error(wc.LOG_GUI, "could not open url %r", url)
        if data and data[0] == 'http error' and data[1] == 404:
            raise IOError(data)
        else:
            raise IOError("no network access available")
    except OSError, data:
        raise IOError, data
    return page


# ====================== end of urlutils.py =================================

def update_filter (wconfig, dryrun=False, log=None):
    """
    Update the given configuration object with .zap files found at baseurl.
    If dryrun is True, only print out the changes but do nothing.

    @raise: IOError
    """
    print >> log, _("updating filters"), "..."
    chg = False
    baseurl = wconfig['baseurl']+"filter/"
    url = baseurl+"filter-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >> log, _("error fetching %s") % url, msg
        print >> log, "...", _("done")
        return chg
    # remember all local config files
    filemap = {}
    for filename in configuration.filterconf_files(wconfig.filterdir):
        filemap[os.path.basename(filename)] = filename
    # read md5sums
    for line in page.read().splitlines():
        if "<" in line:
            print >> log, _("error fetching %s") % url
            print >> log, "...", _("done")
            return chg
        if not line:
            continue
        md5sum, filename = line.split()
        assert filename.endswith('.zap')
        fullname = os.path.join(wconfig.configdir, filename)
        # compare checksums
        if filemap.has_key(filename):
            f = file(fullname)
            data = f.read()
            digest = list(md5.new(data).digest())
            f.close()
            digest = "".join([ "%0.2x"%ord(c) for c in digest ])
            if digest == md5sum:
                print >> log, \
                      _("filter %s not changed, ignoring") % filename
                continue
            print >> log, _("updating filter %s") % filename
        else:
            print >> log, _("adding new filter %s") % filename
        # parse new filter
        url = baseurl + filename
        page = open_url(url)
        parserclass = configuration.confparse.ZapperParser
        p = parserclass(fullname, compile_data=False)
        p.parse(fp=page)
        page.close()
        # compare version compatibility
        if wconfig['configversion'][0] != p.folder.configversion[0]:
            print >> log, _("Incompatible folder version %s, must be %s") % \
                (wconfig['configversion'], p.folder.configversion)
        if wconfig.merge_folder(p.folder, dryrun=dryrun, log=log):
            chg = True
    url = baseurl + "extern-md5sums.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >> log, _("error fetching %s:") % url, msg
        print >> log, "...", _("done")
        return chg
    lines = page.read().splitlines()
    page.close()
    for line in lines:
        if "<" in line:
            print >> log, _("error fetching %s:") % url, \
                          _("invalid content")
            print >> log, "...", _("done")
            return chg
        if not line:
            continue
        md5sum, filename = line.split()
        # XXX UNIX-generated md5sum filenames with subdirs are not portable
        fullname = os.path.join(wconfig.configdir, filename)
        # compare checksums
        if os.path.exists(fullname):
            f = file(fullname)
            data = f.read()
            digest = list(md5.new(data).digest())
            f.close()
            digest = "".join([ "%0.2x"%ord(c) for c in digest ])
            if digest == md5sum:
                print >> log, \
                  _("extern filter %s not changed, ignoring")%filename
                continue
            print >> log, _("updating extern filter %s") % filename
        else:
            print >> log, _("adding new extern filter %s") % filename
        chg = True
        if not dryrun:
            url = baseurl+filename
            try:
                page = open_url(url)
            except IOError, msg:
                print >> log, _("error fetching %s:") % url, msg
                continue
            data = page.read()
            if not data:
                print >> log, _("error fetching %s:") % url, \
                             _("got no data")
                continue
            f = file(fullname, 'wb')
            f.write(data)
            f.close()
    print >> log, "...", _("done")
    return chg


def update_ratings (wconfig, dryrun=False, log=None):
    """
    Update rating database from configured online rating service.
    """
    print >> log, _("updating ratings...")
    chg = False
    baseurl = wconfig['baseurl']+"rating/"
    url = baseurl+"rating.txt"
    try:
        page = open_url(url)
    except IOError, msg:
        print >> log, _("error fetching %s:") % url, msg
        print >> log, "...", _("done")
        return chg
    # Merge new ratings.
    new_ratings = rating.storage.rating_parse(page)
    chg = rating.ratings.merge(new_ratings, dryrun=dryrun, log=log)
    print >> log, "...", _("done")
    return chg
