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

import re, os, sys
import cPickle as pickle
from wc.log import *
from wc import i18n, ConfigDir, AppName
from wc.filter import FilterException

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

def parse (data, debug=0):
    """parse given rating data, throws ParseError on error"""
    categories = {}
    for line in data.splitlines():
        if debug:
            debug(RATING, "Read line %r", line)
        try:
            category, value = line.split(None, 1)
        except ValueError, msg:
            raise ParseError(i18n._("Malformed rating line %r")%line)
        categories[category] = value
    return categories


class ParseError (Exception):
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
    if os.path.isfile(rating_cachefile):
        fp = file(rating_cachefile)
        data = pickle.load(fp)
        fp.close()
        return data
    return {}


rating_cache = rating_cache_load()


def rating_is_cached (url):
    """return True if cache has entry for given url, else False"""
    # XXX norm url ?
    return url in rating_cache


def rating_add (url, rating):
    """add new or update rating in cache and write changes to disk"""
    # XXX norm url ?
    rating_cache[url] = rating
    rating_cache_write()


def rating_allow (url, rule):
    """asks cache if the rule allows the rating data for given url
    Looks up cache to find rating data, if not returns a MISSING message.
    """
    if not rating_is_cached(url):
        return MISSING
    return rule.check_against(rating)


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
