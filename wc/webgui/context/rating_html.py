# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Parameters for rating.html page.
"""

import time as _time
from wc import AppName, Email, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval
from wc.webgui.context import get_prefix_vals as _get_prefix_vals
from wc.url import is_safe_url as _is_safe_url
from wc.strformat import strtime as _strtime
from wc.filter.rating import services, categories
from wc.filter.rating import get_category as _get_category
from wc.filter.rating.rating import Rating as _Rating
from wc.filter.rating.category import intrange_from_string as \
     _intrange_from_string
from wc.filter.rating.category import string_from_intrange as \
     _string_from_intrange
from wc.filter.rating.storage import get_rating_store as _get_rating_store
from wc.filter.rating.storage.pickle import PickleStorage as _PickleStorage

_entries_per_page = 50

# config vars
info = {
    "ratingupdated": False,
    "ratingdeleted": False,
}
error = {
    "categoryvalue": False,
    "selindex": False,
    "url": False,
}
values = {}
rating_modified = {}


def _reset_values ():
    for category in categories:
        if category.iterable:
            values[category.name] = {}
            for value in category.values:
                values[category.name][value] = value=='none'
        else:
            values[category.name] = ""


def _calc_ratings_display ():
    global ratings_display, rating_modified
    urls = rating_store.keys()
    urls.sort()
    ratings_display = urls[curindex:curindex+_entries_per_page]
    rating_modified.clear()
    for _url in ratings_display:
        t = _strtime(rating_store[_url].modified)
        rating_modified[_url] = t.replace(u" ", u"&nbsp;")


_reset_values()
rating_store = _get_rating_store(_PickleStorage)
url = u""
generic = False
# current index of entry to display
curindex = 0
# displayed ratings
ratings_display = []
_calc_ratings_display()
# select range indexes
selindex = []


# form execution
def _exec_form (form, lang):
    global url
    # calculate global vars
    if not _form_url(form):
        return
    if not _form_generic(form):
        return
    if not _form_ratings(form):
        return
    # index stuff
    if form.has_key('selindex'):
        _form_selindex(_getval(form, 'selindex'))
    l = len(rating_store)
    if l > _entries_per_page:
        _calc_selindex(curindex)
    else:
        del selindex[:]
    # generic apply rule values
    if url:
        if form.has_key('apply'):
            _form_apply()
        elif form.has_key('delete'):
            _form_delete()
        else:
            _form_load()
    _calc_ratings_display()


def _form_reset ():
    for key in info.keys():
        info[key] = False
    for key in error.keys():
        error[key] = False
    _reset_values()
    global url, generic, curindex
    url = u""
    generic = False
    curindex = 0


def _form_url (form):
    """Check url validity"""
    global url
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_safe_url(val):
            error['url'] = True
            return False
        url = val
    return True


def _form_generic (form):
    """Check generic validity"""
    global generic
    generic = form.has_key('generic'):
    return True


def _form_ratings (form):
    """Check category value validity"""
    for catname, value in _get_prefix_vals(form, 'category_'):
        category = _get_category(catname)
        if category is None:
            # unknown category
            error['categoryvalue'] = True
            return False
        if category.iterable:
            realvalue = value
        else:
            realvalue = _intrange_from_string(value)
        if not category.valid_value(realvalue):
            error['categoryvalue'] = True
            return False
        if category.iterable:
            values[catname]['none'] = False
            values[catname][value] = True
        else:
            values[catname] = value
    return True


def _form_selindex (index):
    """display entries from given index"""
    global curindex
    try:
        curindex = int(index)
    except ValueError:
        error['selindex'] = True


def _calc_selindex (index):
    global selindex
    res = [index-1000, index-250, index-50, index, index+50,
           index+250, index+1000]
    selindex = [ x for x in res if 0 <= x < len(rating_store) and x!=index ]


def _form_apply ():
    # store rating
    if url in rating_store:
        rating = rating_store[url]
    else:
        rating = _Rating(url, generic)
    rating.remove_categories()
    for catname, value in values.items():
        category = _get_category(catname)
        if category.iterable:
            value = [x for x in value if value[x]][0]
        else:
            value = _intrange_from_string(value)
            if value is None:
                error['ratingupdated'] = True
                return
        rating.add_category_value(category, value)
    rating_store[url] = rating
    try:
        rating_store.write()
        info['ratingupdated'] = True
    except:
        error['ratingupdated'] = True


def _form_delete ():
    global url
    try:
        del rating_store[url]
        rating_store.write()
        info['ratingdeleted'] = True
    except:
        error['ratingdeleted'] = True


def _form_load ():
    global generic, url
    if url in rating_store:
        rating = rating_store[url]
        generic = rating.generic
        for catname, value in rating.category_values.items():
            category = _get_category(catname)
            if category.iterable:
                for x in category.values:
                    values[catname][x] = False
                values[catname][value] = True
            else:
                values[catname] = _string_from_intrange(value)
