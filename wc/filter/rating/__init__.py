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

import re
import urlparse

import wc
import wc.configuration
import wc.log
import wc.url


class RatingParseError (Exception):
    """Raised on parsing errors."""
    pass


def split_url (url):
    """split an url into parts suitable for longest prefix match
       return parts so that "".join(parts) == url
    """
    # split into [scheme, host, path, query, fragment]
    parts = list(urlparse.urlsplit(url))
    if not (parts[0] and parts[1]):
        wc.log.warn(wc.LOG_FILTER, "invalid url for rating split: %r", url)
        return []
    # fix scheme
    parts[0] += ":"
    if parts[0] != 'mailto':
        parts[0] += "//"
    # remove query and fragment
    del parts[3:5]
    # further split path in components
    parts[2:] = split_path(parts[2])
    return parts


def split_path (path):
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




MISSING = _("Unknown page")

is_time = re.compile(r"^\d+$").search


def rating_allow (url, rule):
    """asks cache if the rule allows the rating data for given url
    Looks up cache to find rating data, if not returns a MISSING message.
    """
    rating = rating_cache_get(url)
    if rating is not None:
        return rule.check_against(rating[1])
    return MISSING


def rating_is_valid_value (data, value):
    """return True if given value is valid according to rating data"""
    res = False
    if data["rvalues"]:
        res = value in data["rvalues"]
    elif data["rrange"]:
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
    if prange[0] is not None and \
       value[0] is not None and value[0] < prange[0]:
        return False
    if prange[1] is not None and \
       value[1] is not None and value[1] > prange[1]:
        return False
    return True


_range_re = re.compile(r'^(\d*)-(\d*)$')
def rating_range (value):
    """parse value as range; return tuple (rmin, rmax) or None on error"""
    mo = _range_re.match(value)
    if not mo:
        return None
    vmin, vmax = mo.group(1), mo.group(2)
    if vmin == "":
        vmin = None
    else:
        vmin = int(vmin)
    if vmax == "":
        vmax = None
    else:
        vmax = int(vmax)
    return (vmin, vmax)


def rating_cache_merge (newrating_cache, dryrun=False, log=None):
    """add new ratings, but do not change existing ones"""
    chg = False
    for url, rating in newrating_cache.iteritems():
        if url not in rating_cache:
            chg = True
            print >> log, _("adding new rating for %r") % url
            if not dryrun:
                rating_cache[url] = rating
    if not dryrun and chg:
        rating_cache_write()
    return chg

