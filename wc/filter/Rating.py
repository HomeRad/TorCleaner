# -*- coding: iso-8859-1 -*-
"""rating related data types and routines"""
# Copyright (C) 2004  Bastian Kleineidam
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

import re, os, sys, urlparse
import cPickle as pickle
from wc.log import *
from wc import i18n, ConfigDir, AppName
from wc.url import is_valid_url

MISSING = i18n._("Unknown page")

# rating cache filename
rating_cachefile = os.path.join(ConfigDir, "rating.dat")

# rating associations and their categories
#_base = "http://webcleaner.sourceforge.net"
_base = "http://localhost/~calvin/webcleaner.sf.net/htdocs"
service = dict(
   name = AppName,
   # service homepage
   home = '%s/rating/'%_base,
   # submit ratings to service
   submit = '%s/rating/submit'%_base,
   # request ratings from service
   request = '%s/rating/request'%_base,
   # rating categories
   categories = dict(
       violence = dict(
             name = i18n._('violence'),
             rvalues = ["0", "1", "2"],
           ),
       sex = dict(
             name = i18n._('sex'),
             rvalues = ["0", "1", "2"],
           ),
       language = dict(
             name = i18n._('language'),
             rvalues = ["0", "1", "2"],
           ),
       agerange = dict(
             name = i18n._('age range'),
             rrange = [0, None],
           ),
   ),
)

rangenames = {
    "0": i18n._("None"),
    "1": i18n._("Mild"),
    "2": i18n._("Heavy"),
}

def rating_import (url, ratingdata, debug=0):
    """parse given rating data, throws ParseError on error"""
    categories = {}
    for line in ratingdata.splitlines():
        if debug:
            debug(RATING, "Read line %r", line)
        line = line.strip()
        if not line:
            # ignore empty lines
            continue
        if line.startswith("#"):
            # ignore comments
            continue
        try:
            category, value = line.split(None, 1)
        except ValueError, msg:
            raise RatingParseError(i18n._("malformed rating line %r")%line)
        if category=="modified" and not is_time(value):
            raise RatingParseError(i18n._("malfored modified time %r")%value)
        if category=="generic" and value not in ["true", "false"] and \
           not url.startswith(value):
            raise RatingParseError(i18n._("generic url %r doesn't match %r")%\
                                   (value, url))
        categories[category] = value
    return categories


def rating_export (rating):
    return "\n".join([ "%s %s"%item for item in rating.items() ])


class RatingParseError (Exception):
    """Raised on parsing errors."""
    pass


def rating_cache_write ():
    """write cached rating data to disk"""
    fp = file(rating_cachefile, 'wb')
    pickle.dump(rating_cache, fp, 1)
    fp.close()


def rating_cache_load ():
    """load cached rating data from disk or return an empty cache if no
    cached data is found"""
    global rating_cache
    if os.path.isfile(rating_cachefile):
        fp = file(rating_cachefile)
        rating_cache = pickle.load(fp)
        fp.close()
        # remove invalid entries
        toremove = []
        for url in rating_cache:
            if not is_valid_url(url):
                error(FILTER, "Invalid rating url %r", url)
                toremove.append(url)
        if toremove:
            for url in toremove:
                del rating_cache[url]
            rating_cache_write()


rating_cache = {}
rating_cache_load()


def rating_cache_get (url):
    """return a tuple (url, rating) if cache has entry for given url,
       else None"""
    # use a specialized form of longest prefix matching:
    # split the url in parts and the longest matching part wins
    parts = rating_split_url(url)
    # the range selects from all parts (full url) down to the first two parts
    for i in range(len(parts), 1, -1):
        url = "".join(parts[:i])
        if url in rating_cache:
            return (url, rating_cache[url])
    return None


def rating_split_url (url):
    """split an url into parts suitable for longest prefix match
       return parts so that "".join(parts) == url
    """
    # split into [scheme, host, path, query, fragment]
    parts = list(urlparse.urlsplit(url))
    if not (parts[0] and parts[1]):
        warn(FILTER, "invalid url for rating split: %r", url)
        return []
    # fix scheme
    parts[0] += ":"
    if parts[0]!='mailto':
        parts[0] += "//"
    # remove query and fragment
    del parts[3:5]
    # further split path in components
    parts[2:] = rating_split_path(parts[2])
    return parts


def rating_split_path (path):
    """split a path into parts suitable for longest prefix match
       return parts so that "".join(parts) == path
    """
    parts = [ p for p in path.split("/") if p ]
    if not parts:
        return ['/']
    ret = []
    for p in parts:
        ret.extend(['/', p])
    return ret


def rating_add (url, rating):
    """add new or update rating in cache and write changes to disk"""
    if is_valid_url(url):
        # XXX norm url?
        rating_cache[url] = rating
        rating_cache_write()
    else:
        error(FILTER, "Invalid rating url %r", url)


def rating_allow (url, rule):
    """asks cache if the rule allows the rating data for given url
    Looks up cache to find rating data, if not returns a MISSING message.
    """
    rating = rating_cache_get(url)
    if rating is not None:
        return rule.check_against(rating[1])
    return MISSING


def rating_is_valid_value (data, value):
    res = False
    if data.has_key("rvalues"):
        res = value in data["rvalues"]
    elif data.has_key("rrange"):
        value = rating_range(value)
        if value is None:
            res = False
        else:
            res = rating_in_range(data["rrange"], value)
    return res


def rating_in_range (prange, value):
    """return True iff value is in range
       prange - tuple (min, max)
       value - tuple (min, max)
       """
    if prange[0] is not None and value[0] is not None and value[0]<prange[0]:
        return False
    if prange[1] is not None and value[1] is not None and value[1]>prange[1]:
        return False
    return True


_range_re = re.compile(r'^(\d*)-(\d*)$')
def rating_range (value):
    """parse value as range; return tuple (rmin, rmax) or None on error"""
    mo = _range_re.match(value)
    if not mo:
        return None
    return (mo.group(1), mo.group(2))


if __name__=='__main__':
    for url in ['', 'a', 'a/b',
                'http://imadoofus.com',
                'http://imadoofus.com//',
                'http://imadoofus.com/?q=a',
                'http://imadoofus.com/?q=a#a',
                'http://imadoofus.com/a/b//c',
                'http://imadoofus.com/forum',
                'http://imadoofus.com/forum/',
               ]:
        print rating_split_url(url)
    print rating_cache_get('http://www.heise.de/foren/')
