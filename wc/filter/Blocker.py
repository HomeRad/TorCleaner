# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2007 Bastian Kleineidam
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
Block specific requested URLs.
"""

import re
import os
import gzip
import urllib

import wc.log
import wc.configuration
import wc.url
import wc.filter
import Filter


def is_flash_mime (mime):
    """
    Return True if mime is Shockwave Flash.
    """
    return mime.startswith('application/x-shockwave-flash')


def is_image_mime (mime):
    """
    Return True if mime is an image.
    """
    return mime.startswith('image/')


def is_javascript_mime (mime):
    """
    Return True if mime is JavaScript.
    """
    return mime.startswith('application/x-javascript') or \
           mime.startswith('text/javascript')


def is_html_mime (mime):
    """
    Return True if mime is HTML.
    """
    return mime.startswith('text/html')


# regular expression for image urls
is_image_url = \
     re.compile(r'(?i)\.(gif|jpe?g|ico|png|bmp|pcx|tga|tiff?)$').search
is_flash_url = re.compile(r'(?i)\.(swf|flash)$').search
is_javascript_url = re.compile(r'(?i)\.js$').search


def strblock (block):
    """
    Return string representation of block pattern(s).
    """
    patterns = [ repr(b and b.pattern or "") for b in block ]
    return "[%s]" % ", ".join(patterns)


def append_lines (lines, lst, sid):
    """
    Append lines to given list, augmented with sid.
    """
    for line in lines:
        line = line.strip()
        if not line or line[0] == '#':
            continue
        lst.append((line, sid))


def get_file_data (filename):
    """
    Return plain file object, possible gunzipping the file.
    """
    assert None == wc.log.debug(wc.LOG_FILTER, "reading %s", filename)
    config = wc.configuration.config
    filename = os.path.join(config.configdir, filename)
    if filename.endswith(".gz"):
        f = gzip.GzipFile(filename, 'rb')
    else:
        f = file(filename)
    return f


def try_append_lines (lst, rule):
    """
    Read rule file, print log note on error.
    """
    try:
        lines = get_file_data(rule.filename)
        append_lines(lines, lst, rule.sid)
    except IOError, msg:
        wc.log.error(wc.LOG_FILTER, "could not read file %r: %s",
                     rule.filename, str(msg))


class Blocker (Filter.Filter):
    """
    Block urls and show replacement data instead.
    """

    enable = True

    def __init__ (self):
        """
        Load blocked/allowed urls/regex.
        """
        rulenames = [
            'block',
            'blockdomains',
            'blockurls',
            'allow',
            'allowdomains',
            'allowurls',
        ]
        stages = [wc.filter.STAGE_REQUEST]
        super(Blocker, self).__init__(rulenames=rulenames, stages=stages)
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
        """
        Add rule data to blocker, delegated to add_* methods.
        """
        super(Blocker, self).addrule(rule)
        getattr(self, "add_"+rule.name)(rule)

    def add_allow (self, rule):
        """
        Add AllowRule data.
        """
        if rule.url:
            self.allow.append((re.compile(rule.url), rule.sid))

    def add_block (self, rule):
        """
        Add BlockRule data.
        """
        if rule.url:
            self.block.append((re.compile(rule.url), rule.replacement,
                               rule.sid))

    def add_blockdomains (self, rule):
        """
        Add BlockdomainsRule data.
        """
        try_append_lines(self.blocked_domains, rule)

    def add_allowdomains (self, rule):
        """
        Add AllowdomainsRule data.
        """
        try_append_lines(self.allowed_domains, rule)

    def add_blockurls (self, rule):
        """
        Add BlockurlsRule data.
        """
        try_append_lines(self.blocked_urls, rule)

    def add_allowurls (self, rule):
        """
        Add AllowurlsRule data.
        """
        try_append_lines(self.allowed_urls, rule)

    def doit (self, data, attrs):
        """
        Investigate request data for a block.

        @param data: the complete request (with quoted url),
           we get the unquoted url from args.
        """
        url = attrs['url']
        mime = attrs['mime']
        if not mime:
            mime = "text/html"
        parts = wc.url.url_split(url)
        assert None == wc.log.debug(wc.LOG_FILTER,
                            "block filter working on url %r", url)
        allowed, sid = self.allowed(url, parts)
        if allowed:
            assert None == wc.log.debug(wc.LOG_FILTER,
                                "allowed url %s by rule %s", url, sid)
            return data
        blocked, sid = self.blocked(url, parts)
        if blocked:
            # XXX hmmm, make HTTP HEAD request to get content type???
            assert None == wc.log.debug(wc.LOG_FILTER,
                       "blocked url %s with %s by rule %s", url, blocked, sid)
            if isinstance(blocked, str):
                doc = blocked
            elif isinstance(blocked, unicode):
                doc = blocked.encode("ascii", "ignore")
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
                    wc.log.info(wc.LOG_PROXY,
                      "%r is blocked as HTML but has mime type %r", url, mime)
                doc = self.block_url
                attrs['mime'] = 'text/html'
                rule = [r for r in self.rules if r.sid == sid][0]
                form = {
                    "ruletitle": rule.titles['en'],
                    "selfolder": "%d" % rule.parent.oid,
                    "selrule": "%d" % rule.oid,
                    "blockurl": url,
                }
                query = urllib.urlencode(form)
                doc += "?%s" % query
            port = wc.configuration.config['port']
            if not doc.startswith("http://"):
                doc = "http://localhost:%d%s" % (port, doc)
            return 'GET %s HTTP/1.1' % doc
        return data

    def blocked (self, url, parts):
        """
        True if url is blocked. Parts are the splitted url parts.
        """
        # check blocked domains
        for blockdomain, sid in self.blocked_domains:
            if blockdomain == parts[wc.url.DOMAIN]:
                assert None == wc.log.debug(wc.LOG_FILTER,
                             "blocked by blockdomain %s", blockdomain)
                return True, sid
        # check blocked urls
        for blockurl, sid in self.blocked_urls:
            if blockurl in url:
                assert None == wc.log.debug(wc.LOG_FILTER,
                             "blocked by blockurl %r", blockurl)
                return True, sid
        # check block patterns
        for ro, replacement, sid in self.block:
            mo = ro.search(url)
            if mo:
                assert None == wc.log.debug(wc.LOG_FILTER,
                             "blocked by pattern %s", ro.pattern)
                if replacement:
                    return mo.expand(replacement), sid
                return True, sid
        return False, None

    def allowed (self, url, parts):
        """
        True if url is allowed. Parts are the splitted url parts.
        """
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
