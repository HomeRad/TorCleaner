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
import os
import urlparse
import cPickle as pickle
import wc.i18n
import wc
import wc.log
import wc.url


MISSING = wc.i18n._("Unknown page")

# rating cache filename
rating_cachefile = os.path.join(wc.ConfigDir, "rating.dat")

# rating cache
rating_cache = {}

# rating associations and their categories
service = dict(
   name = wc.AppName,
   # service homepage
   home = '%s/rating/'%wc.Url,
   # submit ratings to service
   submit = '%s/rating/submit'%wc.Url,
   # request ratings from service
   request = '%s/rating/request'%wc.Url,
   # rating categories
   categories = dict(
       violence = dict(
             name = wc.i18n._('violence'),
             rvalues = ["0", "1", "2"],
           ),
       sex = dict(
             name = wc.i18n._('sex'),
             rvalues = ["0", "1", "2"],
           ),
       language = dict(
             name = wc.i18n._('language'),
             rvalues = ["0", "1", "2"],
           ),
       agerange = dict(
             name = wc.i18n._('age range'),
             rrange = [0, None],
           ),
   ),
)

rangenames = {
    "0": wc.i18n._("None"),
    "1": wc.i18n._("Mild"),
    "2": wc.i18n._("Heavy"),
}


is_time = re.compile(r"^\d+$").search

def rating_import (url, ratingdata, debug=0):
    """parse given rating data, throws ParseError on error"""
    categories = {}
    for line in ratingdata.splitlines():
        if debug:
            wc.log.debug(wc.LOG_RATING, "Read line %r", line)
        line = line.strip()
        if not line:
            # ignore empty lines
            continue
        if line.startswith("#"):
            # ignore comments
            continue
        try:
            category, value = line.split(None, 1)
        except ValueError:
            raise RatingParseError(wc.i18n._("malformed rating line %r")%line)
        if category=="modified" and not is_time(value):
            raise RatingParseError(wc.i18n._("malfored modified time %r")%value)
        if category=="generic" and value not in ["true", "false"] and \
           not url.startswith(value):
            raise RatingParseError(wc.i18n._("generic url %r doesn't match %r")%\
                                   (value, url))
        categories[category] = value
    return categories


def rating_export (rating):
    """return string representation of given rating data"""
    return "\n".join([ "%s %s"%item for item in rating.items() ])


def rating_exportall ():
    """export all ratings in a text file called `rating.txt', located
       in the same directory as the file `rating.dat'
    """
    fp = file(os.path.join(wc.ConfigDir, "rating.txt"), 'w')
    for url, rating in rating_cache.iteritems():
        if not wc.url.is_valid_url(url):
            wc.log.error(wc.LOG_RATING, "invalid url %r", url)
            continue
        fp.write("url %s\n"%url)
        fp.write(rating_export(rating))
        fp.write("\n\n")
    fp.close()


class RatingParseError (Exception):
    """Raised on parsing errors."""
    pass


def rating_cache_write ():
    """write cached rating data to disk"""
    fp = file(rating_cachefile, 'wb')
    pickle.dump(rating_cache, fp, 1)
    fp.close()


def rating_cache_load ():
    """load cached rating data from disk and fill the rating_cache.
       If no rating data file is found, do nothing."""
    global rating_cache
    if os.path.isfile(rating_cachefile):
        fp = file(rating_cachefile)
        rating_cache = pickle.load(fp)
        fp.close()
        # remove invalid entries
        toremove = []
        for url in rating_cache:
            if not wc.url.is_valid_url(url):
                wc.log.error(wc.LOG_RATING, "Invalid rating url %r", url)
                toremove.append(url)
        if toremove:
            for url in toremove:
                del rating_cache[url]
            rating_cache_write()


def rating_cache_parse (fp):
    """parse previously exported rating data from given file"""
    url = None
    ratingdata = []
    newrating_cache = {}
    for line in fp:
        line = line.rstrip('\r\n')
        if not line:
            if url:
                data = "\n".join(ratingdata)
                newrating_cache[url] = rating_import(url, data)
            url = None
            ratingdata = []
            continue
        if line.startswith('url'):
            url = line.split()[1]
        elif url:
            ratingdata.append(line)
    return newrating_cache


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
        wc.log.warn(wc.LOG_FILTER, "invalid url for rating split: %r", url)
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
    if wc.url.is_valid_url(url):
        # XXX norm url?
        rating_cache[url] = rating
        rating_cache_write()
    else:
        wc.log.error(wc.LOG_RATING, "Invalid rating url %r", url)


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
    vmin, vmax = mo.group(1), mo.group(2)
    if vmin=="":
        vmin = None
    else:
        vmin = int(vmin)
    if vmax=="":
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
            print >>log, wc.i18n._("adding new rating for %r")%url
            if not dryrun:
                rating_cache[url] = rating
    if not dryrun and chg:
        rating_cache_write()
    return chg


# initialize rating cache
rating_cache_load()
