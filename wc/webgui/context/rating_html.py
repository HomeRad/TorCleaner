# -*- coding: iso-8859-1 -*-
"""parameters for rating.html page"""
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

import time as _time
from wc import AppName, Email, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval
from wc.webgui.context import get_prefix_vals as _get_prefix_vals
from wc.url import is_safe_url as _is_safe_url
from wc.strformat import strtime as _strtime
from wc.filter.rating import services, categories

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
        values[category.name] = {}
        if category.iterable:
            for value in category.values:
                values[category.name][value] = False
        else:
            values[category.name] = None
    rating_modified.clear()


def _calc_ratings_display ():
    global ratings_display
    urls = []#XXXrating_cache.keys()
    urls.sort()
    ratings_display = urls[curindex:curindex+_entries_per_page]
    for _url in ratings_display:
        t = _strtime(float(rating_cache[_url]['modified']))
        rating_modified[_url] = t.replace(u" ", u"&nbsp;")


_reset_values()
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
    l = len(rating_cache)
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
    global url
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_safe_url(val):
            error['url'] = True
            return False
        url = val
    return True


def _form_generic (form):
    global generic
    if form.has_key('generic'):
        generic = True
    return True


def _form_ratings (form):
    for key, value in _get_prefix_vals('category_'):
        category = _get_category(key)
        if not category.is_valid_value(value):
            error['categoryvalue'] = True
            return False
        else:
            ratings[category] = value
            if category not in ["generic", "modified"]:
                values[category] = {value: True}
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
    selindex = [ x for x in res if 0 <= x < len(rating_cache) and x!=index ]


def _form_apply ():
    global url
    rating = {}
    rating.update(ratings)
    if generic:
        rating['generic'] = u"true"
    rating['modified'] = u"%d" % int(_time.time())
    if _rating_add(url, rating):
        info['ratingupdated'] = True
    else:
        error['ratingupdated'] = True


def _form_delete ():
    global url
    if _rating_delete(url):
        info['ratingdeleted'] = True
    else:
        error['ratingdeleted'] = True


def _form_load ():
    global generic, url
    if url in rating_cache:
        rating = rating_cache[url]
        for category, value in rating.items():
            if category == u'generic':
                generic = (value == u'true')
            else:
                ratings[category] = value
                if category not in [u"modified"]:
                    values[category] = {value: True}
