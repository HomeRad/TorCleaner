# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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

from wc import AppName, Email, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval
from wc.webgui.context import get_prefix_vals as _get_prefix_vals
from wc.url import is_safe_url as _is_safe_url
from wc.strformat import strtime as _strtime
from wc.rating.service import ratingservice
from wc.rating.service.ratingformat import intrange_from_string as _intrange_from_string

_entries_per_page = 50

# config vars
info = {
    "ratingupdated": False,
    "ratingdeleted": False,
}
error = {
    "ratingupdated": False,
    "ratingdeleted": False,
    "ratingvalue": False,
    "selindex": False,
    "url": False,
}
values = {}
rating_modified = {}


def _reset_values ():
    """
    Reset rating values.
    """
    for ratingformat in ratingservice.ratingformats:
        if ratingformat.iterable:
            values[ratingformat.name] = {}
            for value in ratingformat.values:
                values[ratingformat.name][value] = (value == 'none')
        else:
            values[ratingformat.name] = ""


def _calc_ratings_display ():
    """
    Calculate current set of ratings to display.
    """
    global ratings_display, rating_modified
    urls = rating_store.keys()
    urls.sort()
    ratings_display = urls[curindex:curindex+_entries_per_page]
    rating_modified.clear()
    for _url in ratings_display:
        t = _strtime(rating_store[_url].modified)
        rating_modified[_url] = t.replace(u" ", u"&nbsp;")


_reset_values()
rating_store = {}#_get_ratings()
url = u""
generic = False
# current index of entry to display
curindex = 0
# displayed ratings
ratings_display = []
_calc_ratings_display()
# select range indexes
selindex = []


def _exec_form (form, lang):
    """
    HTML CGI form handling.
    """
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
    """
    Reset form variables to default values.
    """
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
    """
    Check url validity.
    """
    global url
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_safe_url(val):
            error['url'] = True
            return False
        url = val
    return True


def _form_generic (form):
    """
    Check generic validity.
    """
    global generic
    generic = form.has_key('generic')
    return True


def _form_ratings (form):
    """
    Check rating value validity.
    """
    for catname, value in _get_prefix_vals(form, 'rating_'):
        category = _get_category(catname)
        if category is None:
            # unknown category
            error['ratingvalue'] = True
            return False
        if category.iterable:
            realvalue = value
        else:
            realvalue = _intrange_from_string(value)
        if not category.valid_value(realvalue):
            error['ratingvalue'] = True
            return False
        if category.iterable:
            values[catname]['none'] = False
            values[catname][value] = True
        else:
            values[catname] = value
    return True


def _form_selindex (index):
    """
    Display entries from given index.
    """
    global curindex
    try:
        curindex = int(index)
    except ValueError:
        error['selindex'] = True


def _calc_selindex (index):
    """
    Calculate ratings selection index.
    """
    global selindex
    res = [index-1000, index-250, index-50, index, index+50,
           index+250, index+1000]
    selindex = [ x for x in res if 0 <= x < len(rating_store) and x!=index ]


def _form_apply ():
    """
    Store changed ratings.
    """
    rating = _Rating(url, generic)
    rating.remove_categories()
    for catname, value in values.iteritems():
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
    """
    Delete rating.
    """
    global url
    try:
        del rating_store[url]
        rating_store.write()
        info['ratingdeleted'] = True
    except:
        error['ratingdeleted'] = True


def _form_load ():
    """
    Load ratings.
    """
    global generic, url
    if url in rating_store:
        rating = rating_store[url]
        generic = rating.generic
        for catname, value in rating.category_values.iteritems():
            category = _get_category(catname)
            if category.iterable:
                for x in category.values:
                    values[catname][x] = False
                values[catname][value] = True
            else:
                values[catname] = _string_from_intrange(value)
