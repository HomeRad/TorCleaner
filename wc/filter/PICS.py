# -*- coding: iso-8859-1 -*-
"""Parse and filter PICS data.
See http://www.w3.org/PICS/labels.html for more info.
"""
# Copyright (C) 2003-2004  Bastian Kleineidam
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

import re, os
import cPickle as pickle
from wc.log import *
from wc import i18n, ConfigDir, AppName
from wc.filter import FilterException


class FilterPics (FilterException):
    """Raised when filter detected PICS rated content.
       Proxy must not have sent any content.
    """
    MISSING = i18n._("Unknown page")
    def isPicsMissing (self):
        return str(self)==FilterPics.MISSING


# PICS rating associations and their categories
services = {}

pics_cachefile = os.path.join(ConfigDir, "pics.dat")

def pics_cache_write ():
    """write cached pics data to disk"""
    fp = file(pics_cachefile, 'wb')
    pickle.dump(pics_cache, fp, 1)
    fp.close()


def pics_cache_load ():
    """load cached pics data from disk or return an empty cache if no
    cached data is found"""
    if os.path.isfile(pics_cachefile):
        fp = file(pics_cachefile)
        data = pickle.load(fp)
        fp.close()
        return data
    return {}

pics_cache = pics_cache_load()

def pics_is_cached (url):
    """return True iff PICS cache has entry for given url"""
    if url in pics_cache:
        # exact match
        return pics_cache[url]
    for key in pics_cache.keys():
        if url.startswith(key) and pics_cache[key].generic:
            # prefix match
            return pics_cache[key]
    return None


def pics_add (url, data):
    """add new PICS data for given url in cache and write changes to disk"""
    pics_cache[url] = data
    pics_cache_write()


def pics_allow (url, rule):
    """asks cache if the rule allows the PICS data for given url
    Looks up cache to find PICS data, if not find will not allow the url
    """
    entry = pics_is_cached(url)
    if entry is None:
        return FilterPics.MISSING
    return check_pics(rule, entry)


_range_re = re.compile(r'^(\d*)-(\d*)$')
def pics_is_valid_value (data, value):
    if data["type"]=='int':
        try:
            value = int(value)
        except ValueError:
            return False
        return (data["range"][0] <= value <= data["range"][1])
    if data["type"]=='range':
        mo = _range_re.match(value)
        if not mo:
            return False
        rmin, rmax = mo.group(1), mo.group(2)
        if data["range"][0] is not None and rmin is not None and \
           rmin < data["range"][0]:
            return False
        if data["range"][1] is not None and rmax is not None and \
           rmax > data["range"][1]:
            return False
        return True
    return False


# rating phrase searcher
ratings = re.compile(r'r(atings)?\s*\((?P<rating>[^)]*)\)').finditer

def check_pics_rule (pics, rule):
    """check PICS labels according to given PicsRule

       rule - the PicsRule object to check against
       pics - the PICS label data

       return -  non-empty match message if some rating exceeds the
                 configured rule rating levels,
                 else None
    """
    # check all in the rule configured PICS services
    for service, categories in rule.ratings.items():
        if pics.service == service:
            for category, data in categories.items():
                if category in pics.categories:
                    value = pics.categories[category].value
                    if pics_in_range(data, value):
                        return i18n._("PICS %s match") % category
    # no match
    return None


services['webcleaner'] = dict(
   name = AppName,
   # service homepage
   home = 'http://webcleaner.sourceforge.net/pics/',
   # submit ratings to service
   submit = 'http://webcleaner.sourceforge.net/pics/submit',
   # request ratings from service
   request = 'http://webcleaner.sourceforge.net/pics/request',
   # rating categories
   # rating values are 0: None, 1: mild, 2: heavy
   # age range is 0-.., for example "5-10" or "14-"
   categories = dict(
       v = dict(
             name = i18n._('violence'),
             type = 'int',
             range = [0,2],
           ),
       s = dict(
             name = i18n._('sex'),
             type = 'int',
             range = [0,2],
           ),
       l = dict(
             name = i18n._('language'),
             type = 'int',
             range = [0,2],
           ),
       o = dict(
             name = i18n._('other'),
             type = 'int',
             range = [0,2],
           ),
       a = dict(
             name = i18n._('age range'),
             type = 'range',
             range = [0,None],
           ),
   ),
)


def _test ():
    from wc.filter.rules.PicsRule import PicsRule
    labellist = """
(PICS-1.1
 "http://webcleaner.sourceforge.net/pics/"
 labels
     generic true for "http://kampfesser.net/"
     ratings (a 10-)
     generic true for http://rotten.com/"
     ratings (v 2 l 2 s 2)
 """
    rule = PicsRule()
    print check_pics(rule, labellist)


if __name__=='__main__':
    _test()

