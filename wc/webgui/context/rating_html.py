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
from wc import AppName, Email, Version, ConfigDir, config
from wc.webgui.context import getval as _getval
from wc.filter.Rating import service, rangenames, rating_cache
from wc.filter.Rating import rating_cache_write as _rating_cache_write
from wc.filter.Rating import rating_is_valid_value as _rating_is_valid_value
from wc.url import is_valid_url as _is_valid_url
from wc.strformat import strtime as _strtime

_entries_per_page = 50

def _reset_ratings ():
    ratings.clear()
    for category, catdata in service['categories'].items():
        if catdata.get('rvalues'):
            ratings[category] = catdata['rvalues'][0]
        else:
            ratings[category] = ""
    values.clear()
    for category, value in ratings.items():
        if category not in ["generic", "modified"]:
            values[category] = {value: True}
    rating_modified.clear()


def _calc_ratings_display ():
    global ratings_display
    urls = rating_cache.keys()
    urls.sort()
    ratings_display = urls[curindex:curindex+_entries_per_page]
    for _url in ratings_display:
        t = _strtime(float(rating_cache[_url]['modified']))
        rating_modified[_url] = t.replace(u" ", u"&nbsp;")


# config vars
info = {}
error = {}
ratings = {}
values = {}
rating_modified = {}
_reset_ratings()
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
    # reset info/error and form vals
    _form_reset()
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
    info.clear()
    error.clear()
    _reset_ratings()
    global url, generic, curindex
    url = u""
    generic = False
    curindex = 0


def _form_url (form):
    global url
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_valid_url(val):
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
    for category, catdata in service['categories'].items():
        key = 'category_%s'%category
        if form.has_key(key):
            value = _getval(form, key)
            if not _rating_is_valid_value(catdata, value):
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
    res = [index-1000, index-250, index-50, index, index+50, index+250, index+1000]
    selindex = [ x for x in res if 0 <= x < len(rating_cache) and x!=index ]


def _form_apply ():
    global url
    rating = {}
    rating.update(ratings)
    if generic:
        rating['generic'] = u"true"
    rating['modified'] = u"%d"%int(_time.time())
    rating_cache[url] = rating
    _rating_cache_write()
    info['ratingupdated'] = True


def _form_delete ():
    global url
    del rating_cache[url]
    _rating_cache_write()
    info['ratingdeleted'] = True


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
