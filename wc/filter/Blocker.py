# -*- coding: iso-8859-1 -*-
"""block specific URLs"""
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

import re, os, gzip, urllib
from wc.filter import FILTER_REQUEST
from wc.filter.Filter import Filter
from wc import ConfigDir, config
from wc.log import *
from wc.url import DOMAIN, spliturl

# regular expression for image filenames
is_image = re.compile(r'(?i)\.(gif|jpe?g|ico|png|bmp|pcx|tga|tiff?)$').search

def strblock (block):
    patterns = [ repr(b and b.pattern or "") for b in block ]
    return "[%s]" % ", ".join(patterns)


class Blocker (Filter):
    """block urls and show replacement data instead"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_REQUEST]
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


    def addrule (self, rule):
        super(Blocker, self).addrule(rule)
        getattr(self, "add_"+rule.get_name())(rule)


    def add_allow (self, rule):
        self.allow.append((re.compile(rule.url), rule.sid))


    def add_block (self, rule):
        self.block.append((re.compile(rule.url), rule.replacement, rule.sid))


    def add_blockdomains (self, rule):
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.blocked_domains.append((line, rule.sid))


    def add_allowdomains (self, rule):
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.allowed_domains.append((line, rule.sid))


    def add_blockurls (self, rule):
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.blocked_urls.append((line, rule.sid))


    def add_allowurls (self, rule):
        for line in self.get_file_data(rule.filename):
            line = line.strip()
            if not line or line[0]=='#':
                continue
            self.allowed_urls.append((line, rule.sid))


    def get_file_data (self, filename):
        debug(FILTER, "reading %s", filename)
        filename = os.path.join(ConfigDir, filename)
        if filename.endswith(".gz"):
            f = gzip.GzipFile(filename, 'rb')
        else:
            f = file(filename)
        return f


    def doit (self, data, **args):
        """investigate request data for a block.
           data is the complete request (with quoted url),
           we get the unquoted url from args
        """
        url = args['url']
        parts = spliturl(url)
        debug(FILTER, "block filter working on url %r", url)
        allowed, sid = self.allowed(url, parts)
        if allowed:
            debug(FILTER, "allowed url %s by rule %s", url, sid)
            return data
        blocked, sid = self.blocked(url, parts)
        if blocked:
            debug(FILTER, "blocked url %s by rule %s", url, sid)
            if isinstance(blocked, basestring):
                doc = blocked
            elif is_image(url):
                doc = self.block_image
            else:
                # XXX hmmm, what about CGI images, make HTTP HEAD request?
                doc = self.block_url
                rule = [r for r in self.rules if r.sid==sid][0]
                query = urllib.urlencode({"rule": rule.tiptext(),
                                          "selfolder": "%d"%rule.parent.oid,
                                          "selrule": "%d"%rule.oid})
                doc += "?%s" % query
            port = config['port']
            # XXX handle https requests here?
            return 'GET http://localhost:%d%s HTTP/1.1' % (port, doc)
        return data


    def blocked (self, url, parts):
        # check blocked domains
        for blockdomain, sid in self.blocked_domains:
            if blockdomain == parts[DOMAIN]:
                debug(FILTER, "blocked by blockdomain %s", blockdomain)
                return True, sid
        # check blocked urls
        for blockurl, sid in self.blocked_urls:
            if blockurl in url:
                debug(FILTER, "blocked by blockurl %s", blockurl)
                return True, sid
        # check block patterns
        for ro, replacement, sid in self.block:
            mo = ro.search(url)
            if mo:
                debug(FILTER, "blocked by pattern %s", ro.pattern)
                if replacement:
                    return mo.expand(replacement), sid
                return True, sid
        return False, None


    def allowed (self, url, parts):
        for allowdomain, sid in self.allowed_domains:
            if allowdomain == parts[DOMAIN]:
                return True, sid
        for allowurl, sid in self.allowed_urls:
            if allowurl in url:
                return True, sid
        for ro, sid in self.allow:
            mo = ro.search(url)
            if mo:
                return True, sid
        return False, None
