"""block specific URLs"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
import re, urlparse, os, wc
from Rules import Netlocparts
from wc.filter import FILTER_REQUEST, Filter
from wc import debug
from wc.debug_levels import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_REQUEST]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['block','allow']
mimelist = []
# regular expression for image filenames
image_re=re.compile(r'\.(?i)(gif|jpg|png)')

def strblock (block):
    s="("
    for b in block:
        s = s + ","+(b and b.pattern or "")
    return s+")"

def _file_url (fname):
    u = os.path.join(wc.ConfigDir, fname)
    u = os.path.normcase(u).replace("\\", "/")
    return "file://"+u


class Blocker (Filter):

    def __init__ (self, mimelist):
        """With no blocker and no allower we never block."""
        Filter.__init__(self, mimelist)
        from os.path import join
        self.block = []
        self.allow = []
        self.blocked_url = _file_url("blocked.html")
        self.blocked_image = _file_url("blocked.gif")

    def addrule (self, rule):
        Filter.addrule(self, rule)
        _rule = []
        for part in Netlocparts:
            _rule.append(getattr(rule, part))
        _rule = map(lambda x: x and re.compile(x) or None, _rule)
        # append the block url (if any)
        _rule.append(rule.url)
        getattr(self, rule.get_name()).append(_rule)

    def doit (self, data, **args):
        debug(HURT_ME_PLENTY, "block filter working on %s" % `data`)
        splitted = data.split()
        if len(splitted)==3:
            method,url,protocol = splitted
            urlTuple = list(urlparse.urlparse(url))
            netloc = urlTuple[1]
            s = netloc.split(":")
            if len(s)==2:
                urlTuple[1:2] = s
            else:
                urlTuple[1:2] = [netloc,80]
            blocked = self.blocked(urlTuple)
            if blocked is not None:
                debug(BRING_IT_ON, "blocked url %s" % url)
                # index 3, not 2!
                if image_re.match(urlTuple[3][-4:]):
                    return '%s %s %s' % (method,
		           blocked or self.blocked_image, 'image/gif')
                else:
                    # XXX hmmm, what about CGI images?
                    # make HTTP request?
                    return '%s %s %s' % (method,
                           blocked or self.blocked_url, 'text/html')
        return data

    def blocked (self, urlTuple):
        for _block in self.block:
            match = 1
            for i in range(len(urlTuple)):
                if _block[i]:
                    debug(NIGHTMARE, "block pattern "+_block[i].pattern)
                    if not _block[i].search(urlTuple[i]):
                        debug(NIGHTMARE, "no match")
                        match = 0
            if match and not self.allowed(urlTuple):
                debug(HURT_ME_PLENTY, "blocked", urlTuple, "with", _block[-1])
                return _block[-1]
        return None

    def allowed (self, urlTuple):
        for _allow in self.allow:
            match = 1
            for i in range(len(urlTuple)):
                if _allow[i]:
                    debug(NIGHTMARE, "allow pattern "+_allow[i].pattern)
		    if not _allow[i].search(urlTuple[i]):
                        debug(NIGHTMARE, "no match")
                        match = 0
            if match:
                debug(NIGHTMARE, "allowed")
	        return 1
        return 0
