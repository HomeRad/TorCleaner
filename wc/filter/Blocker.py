# -*- coding: iso-8859-1 -*-
"""block specific requested URLs"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import re
import os
import gzip
import urllib
import wc
import wc.url
import wc.filter
import wc.filter.Filter


def is_flash_mime (mime):
    """return True if mime is Shockwave Flash"""
    return mime.startswith('application/x-shockwave-flash')


def is_image_mime (mime):
    """return True if mime is an image"""
    return mime.startswith('image/')


def is_javascript_mime (mime):
    """return True if mime is JavaScript"""
    return mime.startswith('application/x-javascript') or \
           mime.startswith('text/javascript')


def is_html_mime (mime):
    """return True if mime is HTML"""
    return mime.startswith('text/html')


# regular expression for image urls
is_image_url = re.compile(r'(?i)\.(gif|jpe?g|ico|png|bmp|pcx|tga|tiff?)$').search
is_flash_url = re.compile(r'(?i)\.(swf|flash)$').search
is_javascript_url = re.compile(r'(?i)\.js$').search


def strblock (block):
    """return string representation of block pattern(s)"""
    patterns = [ repr(b and b.pattern or "") for b in block ]
    return "[%s]" % ", ".join(patterns)


class Blocker (wc.filter.Filter.Filter):
    """block urls and show replacement data instead"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_REQUEST]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = [
        'block',
        'blockdomains',
        'blockurls',
        'allow',
        'allowdomains',
        'allowurls',
    ]
    mimelist = []

    def __init__ (self):
        """load blocked/allowed urls/regex."""
        super(Blocker, self).__init__()
        # block and allow regular expressions
        self.block = []
        self.allow = []
        # blocked domains (exact host match)
        self.blocked_domains = []
        # blocked urls (exact host match, prefix url match)
        self.blocked_urls = []
        # allowed domains (exact host match)
        self.allowed_domains = []
        # allowed urls (exact host match, prefix url match)
        self.allowed_urls = []
        # urls for blocked types
        self.block_url = "/blocked.html"
        self.block_image = "/blocked.png"
        self.block_flash = "/blocked.swf"
        self.block_js = "/blocked.js"


    def addrule (self, rule):
        """add rule data to blocker, delegated to add_* methods"""
        super(Blocker, self).addrule(rule)
        getattr(self, "add_"+rule.get_name())(rule)


    def add_allow (self, rule):
        """add AllowRule data"""
        if rule.url:
            self.allow.append((re.compile(rule.url), rule.sid))


    def add_block (self, rule):
        """add BlockRule data"""
        if rule.url:
            self.block.append((re.compile(rule.url), rule.replacement, rule.sid))


    def add_blockdomains (self, rule):
        """add BlockdomainsRule data"""
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.blocked_domains.append((line, rule.sid))


    def add_allowdomains (self, rule):
        """add AllowdomainsRule data"""
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.allowed_domains.append((line, rule.sid))


    def add_blockurls (self, rule):
        """add BlockurlsRule data"""
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.blocked_urls.append((line, rule.sid))


    def add_allowurls (self, rule):
        """add AllowurlsRule data"""
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.allowed_urls.append((line, rule.sid))


    def get_file_data (self, filename):
        """return plain file object, possible gunzipping the file"""
        wc.log.debug(wc.LOG_FILTER, "reading %s", filename)
        filename = os.path.join(wc.ConfigDir, filename)
        if filename.endswith(".gz"):
            f = gzip.GzipFile(filename, 'rb')
        else:
            f = file(filename)
        return f


    def doit (self, data, **attrs):
        """investigate request data for a block.
           data is the complete request (with quoted url),
           we get the unquoted url from args
        """
        url = attrs['url']
        mime = attrs['mime']
        if mime is None:
            mime = "text/html"
        parts = wc.url.spliturl(url)
        wc.log.debug(wc.LOG_FILTER, "block filter working on url %r", url)
        allowed, sid = self.allowed(url, parts)
        if allowed:
            wc.log.debug(wc.LOG_FILTER, "allowed url %s by rule %s", url, sid)
            return data
        blocked, sid = self.blocked(url, parts)
        if blocked:
            # XXX hmmm, make HTTP HEAD request to get content type???
            wc.log.debug(wc.LOG_FILTER, "blocked url %s by rule %s", url, sid)
            if isinstance(blocked, basestring):
                doc = blocked
            elif is_image_mime(mime) or is_image_url(url):
                doc = self.block_image
                attrs['mime'] = 'image/png'
            elif is_flash_mime(mime) or is_flash_url(url):
                doc = self.block_flash
                attrs['mime'] = 'application/x-shockwave-flash'
            elif is_javascript_mime(mime) or is_javascript_url(url):
                doc = self.block_js
                attrs['mime'] = 'application/x-javascript'
            else:
                if not is_html_mime(mime):
                    wc.log.warn(wc.LOG_PROXY, "%r is blocked as HTML but has mime type %r", url, mime)
                doc = self.block_url
                attrs['mime'] = 'text/html'
                rule = [r for r in self.rules if r.sid==sid][0]
                query = urllib.urlencode({"rule": rule.tiptext(),
                                          "selfolder": "%d"%rule.parent.oid,
                                          "selrule": "%d"%rule.oid})
                doc += "?%s" % query
            port = wc.config['port']
            # XXX activate when https can be served locally
            #if url.startswith("https://"):
            #    scheme = "https"
            #else:
            #    scheme = "http"
            scheme = "http"
            return 'GET %s://localhost:%d%s HTTP/1.1' % (scheme, port, doc)
        return data


    def blocked (self, url, parts):
        """return True if url is blocked. Parts are the splitted url parts."""
        # check blocked domains
        for blockdomain, sid in self.blocked_domains:
            if blockdomain == parts[wc.url.DOMAIN]:
                wc.log.debug(wc.LOG_FILTER, "blocked by blockdomain %s", blockdomain)
                return True, sid
        # check blocked urls
        for blockurl, sid in self.blocked_urls:
            if blockurl in url:
                wc.log.debug(wc.LOG_FILTER, "blocked by blockurl %s", blockurl)
                return True, sid
        # check block patterns
        for ro, replacement, sid in self.block:
            mo = ro.search(url)
            if mo:
                wc.log.debug(wc.LOG_FILTER, "blocked by pattern %s", ro.pattern)
                if replacement:
                    return mo.expand(replacement), sid
                return True, sid
        return False, None


    def allowed (self, url, parts):
        """return True if url is allowed. Parts are the splitted url parts."""
        for allowdomain, sid in self.allowed_domains:
            if allowdomain == parts[wc.url.DOMAIN]:
                return True, sid
        for allowurl, sid in self.allowed_urls:
            if allowurl in url:
                return True, sid
        for ro, sid in self.allow:
            mo = ro.search(url)
            if mo:
                return True, sid
        return False, None

