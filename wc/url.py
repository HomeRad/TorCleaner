# -*- coding: iso-8859-1 -*-
"""url utils"""
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

import re, urlparse, os
from urllib import splittype, splithost, splitnport, splitquery, quote, unquote
from wc import ip

# adapted from David Wheelers "Secure Programming for Linux and Unix HOWTO"
_basic = {
    "_az09": r"a-z0-9",
    "_path": r"\-\_\.\!\~\*\'\(\)",
    "_hex_safe": r"2-9a-f",
    "_hex_full": r"0-9a-f",
}
_safe_char = r"([%(_az09)s%(_path)s\+]|(%%[%(_hex_safe)s][%(_hex_full)s]))"%_basic
_safe_scheme_pattern = r"(https?|ftp)"
_safe_host_pattern = r"([%(_az09)s][%(_az09)s\-]*(\.[%(_az09)s][%(_az09)s\-]*)*\.?)"%_basic
_safe_path_pattern = r"((/([%(_az09)s%(_path)s]|(%%[%(_hex_safe)s][%(_hex_full)s]))+)*/?)"%_basic
_safe_fragment_pattern = r"%s*"%_safe_char
_safe_cgi = r"%s+(=%s+)?" % (_safe_char, _safe_char)
_safe_query_pattern = r"(%s(&%s)*)?"%(_safe_cgi, _safe_cgi)
safe_url_pattern = r"%s://%s%s(#%s)?" % \
    (_safe_scheme_pattern, _safe_host_pattern,
     _safe_path_pattern, _safe_fragment_pattern)

is_valid_url = re.compile("(?i)^%s$"%safe_url_pattern).match
is_valid_host = re.compile("(?i)^%s$"%_safe_host_pattern).match
is_valid_path = re.compile("(?i)^%s$"%_safe_path_pattern).match
is_valid_query = re.compile("(?i)^%s$"%_safe_query_pattern).match
is_valid_fragment = re.compile("(?i)^%s$"%_safe_fragment_pattern).match

def is_valid_js_url (urlstr):
    """test javascript urls"""
    url = urlparse.urlsplit(urlstr)
    if url[0].lower()!='http':
        print 1
        return False
    if not is_valid_host(url[1]):
        print 2
        return False
    if not is_valid_path(url[2]):
        print 3
        return False
    if not is_valid_query(url[3]):
        print 4
        return False
    if not is_valid_fragment(url[4]):
        print 5
        return False
    return True


def safe_host_pattern (host):
    return "(?i)%s://%s%s(#%s)?" % \
     (_safe_scheme_pattern, host, _safe_path_pattern, _safe_fragment_pattern)


# XXX better name/implementation for this function
def stripsite (url):
    """remove scheme and host from url. return host, newurl"""
    url = urlparse.urlsplit(url)
    return url[1], urlparse.urlunsplit( (0,0,url[2],url[3],url[4]) )


def url_norm (url):
    """unquote and normalize url which must be quoted"""
    urlparts = list(urlparse.urlsplit(url))
    urlparts[0] = unquote(urlparts[0])
    urlparts[1] = unquote(urlparts[1])
    urlparts[2] = unquote(urlparts[2])
    urlparts[4] = unquote(urlparts[4])
    path = urlparts[2].replace('\\', '/')
    if not path or path=='/':
        urlparts[2] = '/'
    else:
        # XXX this works only under windows and posix??
        # collapse redundant path segments
        urlparts[2] = os.path.normpath(path).replace('\\', '/')
        if path.endswith('/'):
            urlparts[2] += '/'
    return urlparse.urlunsplit(urlparts)


def url_quote (url):
    """quote given url"""
    urlparts = list(urlparse.urlsplit(url))
    urlparts[0] = quote(urlparts[0])
    urlparts[1] = quote(urlparts[1], ':')
    urlparts[2] = quote(urlparts[2], '/')
    urlparts[4] = quote(urlparts[4])
    return urlparse.urlunsplit(urlparts)


def document_quote (document):
    """quote given document"""
    doc, query = splitquery(document)
    doc = quote(doc, '/')
    if query:
        return "%s?%s" % (doc, query)
    return doc


def match_url (url, domainlist):
    if not url:
        return False
    return match_host(spliturl(url)[1], domainlist)


def match_host (host, domainlist):
    if not host:
        return False
    for domain in domainlist:
        if host.endswith(domain):
            return True
    return False


default_ports = {
    'http' : 80,
    'https' : 443,
    'nntps' : 563,
}

def spliturl (url):
    """split url in a tuple (scheme, hostname, port, document) where
    hostname is always lowercased
    precondition: url is syntactically correct URI (eg has no whitespace)"""
    scheme, netloc = splittype(url)
    host, document = splithost(netloc)
    port = default_ports.get(scheme, 80)
    if host:
        host = host.lower()
        host, port = splitnport(host, port)
    return scheme, host, port, document


# constants defining url part indexes
SCHEME = 0
HOSTNAME = DOMAIN = 1
PORT = 2
DOCUMENT = 3
