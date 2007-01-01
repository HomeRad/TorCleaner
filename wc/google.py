# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2007 Bastian Kleineidam
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
Google utility functions.
"""

import urllib
import urlparse

google_domain = "http://www.google.com"

# list of http status codes when to try google
google_try_status = (410, 503, 504, )

def get_google_cache_url (url):
    """
    Return google cache url for given url.
    """
    return "%s/search?q=cache:%s" % (google_domain, urllib.quote_plus(url))


def get_google_search_url (query):
    """
    Return google search url for given url.
    """
    return "%s/search?q=%s" % (google_domain, query)


def get_google_clean_url (url):
    """
    Google ignores scheme, query and anchor parts when caching urls.
    Additionally it ignores unusual filenames from urls
    (example: http://slashdot.org/index.pl is not found in cache,
    but http.//slashdot.org/ is found)
    So this function does the following:
     - remove scheme, query and anchor from url
     - if path does not end with ".html" or "/", replace the path with
       the root path "/"
    """
    parts = urlparse.urlsplit(url)
    if not parts[2].endswith(".html") and not parts[2].endswith("/"):
        path = "/"
    else:
        path = parts[2]
    # use only host and path (ie remove scheme, query and fragment)
    return parts[1]+path


def get_google_context (url, response):
    """
    Return google template context for given url and response data.
    """
    url_parts = urlparse.urlsplit(url)
    context = {
      'url': url,
      'response': response,
      'site': url_parts[1],
      'path': url_parts[2],
      'cache_site': get_google_cache_url("http://%s/" % url_parts[1]),
      'cache_path': get_google_cache_url("http://%s%s" % url_parts[1:3]),
      'coral_path': ("http://%s.nyud.net:8090%s" % url_parts[1:3]),
    }
    return context
