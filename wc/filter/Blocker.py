"""block specific URLs"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

import re, urlparse, os, gzip
from wc.filter.rules.AllowRule import Netlocparts
from wc.filter import FILTER_REQUEST
from wc.filter.Filter import Filter
from wc import ConfigDir, config
from wc.log import *

# regular expression for image filenames
is_image = re.compile(r'^(?i)\.(gif|jpe?g|ico|png|bmp|pcx|tga|tiff?)$').search

def strblock (block):
    patterns = [ repr(b and b.pattern or "") for b in block ]
    return "[%s]" % ", ".join(patterns)


class Blocker (Filter):
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
	# strict whitelist mode (for parents)
	self.strict_whitelist = config['strict_whitelist']


    def addrule (self, rule):
        super(Blocker, self).addrule(rule)
        getattr(self, "add_"+rule.get_name())(rule)


    def add_allow (self, rule):
        self.allow.append(self.get_netloc_rule(rule))


    def add_block (self, rule):
        _rule = self.get_netloc_rule(rule)
        # append the block url (if any)
        _rule.append(rule.url)
        self.block.append(_rule)


    def get_netloc_rule (self, rule):
        _rule = []
        for part in Netlocparts:
            x = getattr(rule, part)
            if x:
                _rule.append(re.compile(x))
            else:
                _rule.append(None)
        return _rule


    def add_blockdomains (self, rule):
        lines = self.get_file_data(rule.filename)
        for line in lines:
            line = line.strip()
            if not line or line[0]=='#': continue
            self.blocked_domains.append(line)


    def add_allowdomains (self, rule):
        lines = self.get_file_data(rule.filename)
        for line in lines:
            line = line.strip()
            if not line or line[0]=='#': continue
            self.allowed_domains.append(line)


    def add_blockurls (self, rule):
        lines = self.get_file_data(rule.filename)
        for line in lines:
            line = line.strip()
            if not line or line[0]=='#': continue
            self.blocked_urls.append(line.split("/", 1))


    def add_allowurls (self, rule):
        lines = self.get_file_data(rule.filename)
        for line in lines:
            line = line.strip()
            if not line or line[0]=='#': continue
            self.allowed_urls.append(line.split("/", 1))


    def get_file_data (self, filename):
        debug(FILTER, "reading %s", filename)
        filename = os.path.join(ConfigDir, filename)
        if filename.endswith(".gz"):
            f = gzip.GzipFile(filename, 'rb')
        else:
            f = file(filename)
        return f.readlines()


    def doit (self, data, **args):
        debug(FILTER, "block filter working on %s", `data`)
        urlTuple = list(urlparse.urlparse(data))
        netloc = urlTuple[1]
        s = netloc.split(":")
        if len(s)==2:
            urlTuple[1:2] = s
        else:
            urlTuple[1:2] = [netloc,80]
        if self.allowed(urlTuple):
            return data
        blocked = self.strict_whitelist or self.blocked(urlTuple)
        if blocked is not False:
            debug(FILTER, "blocked url %s", data)
            # index 3, not 2!
            if blocked:
                doc = blocked
            elif is_image(urlTuple[3][-4:]):
                doc = self.block_image
            else:
                # XXX hmmm, what about CGI images?
                # make HTTP HEAD request?
                doc = self.block_url
            port = config['port']
            return 'http://localhost:%d%s' % (port, doc)
        return data


    def blocked (self, urlTuple):
        # check blocked domains
        for _block in self.blocked_domains:
            if urlTuple[1] == _block:
                return False
        # check blocked urls
        for _block in self.blocked_urls:
            if urlTuple[1]==_block[0] and urlTuple[3].startswith(_block[1]):
                return False
        # check block patterns
        for _block in self.block:
            match = True
            for i in range(len(urlTuple)):
                if _block[i] and not _block[i].search(urlTuple[i]):
                    match = False
                    break
            if match:
                debug(FILTER, "blocked %s\n         with %s", urlTuple,
                      strblock(_block))
                return _block[-1]
        return False


    def allowed (self, urlTuple):
        for _allow in self.allowed_domains:
            if urlTuple[1] == _allow:
                return True
        for _allow in self.allowed_urls:
            if urlTuple[1]==_allow[0] and urlTuple[3].startswith(_allow[1]):
                return True
        for _allow in self.allow:
            match = True
            for i in range(len(urlTuple)):
                if _allow[i]:
		    if not _allow[i].search(urlTuple[i]):
                        match = False
            if match:
                debug(FILTER, "allowed %s", str(urlTuple))
	        return True
        return False
