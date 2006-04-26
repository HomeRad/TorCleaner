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
"""Parameters for rating.html page."""

from wc import AppName, Email, Version
from wc.configuration import config
from wc.configuration.ratingstorage import make_safe_url as _make_safe_url
from wc.containers import CaselessDict as _CaselessDict
from wc.webgui.context import getval as _getval
from wc.webgui.context import get_prefix_vals as _get_prefix_vals
from wc.url import is_safe_url as _is_safe_url
from wc.strformat import strtime as _strtime
from wc.rating.service import ratingservice
from wc.rating.service.ratingformat import parse_range as _parse_range
from wc.rating import Rating as _Rating
from wc.rating.service.urlrating import WcUrlRating as _WcUrlRating

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
# rating data
url = u""
generic = False
rating = _Rating()
rating_store = config['rating_storage']
# current index of entry to display
curindex = 0
# displayed ratings
ratings_display = []
# rating data for cgi display
cgi_rating = _CaselessDict()
rating_modified = {}
# select range indexes
selindex = []

def _reset_cgi_rating ():
    """Reset CGI rating values."""
    for ratingformat in ratingservice.ratingformats:
        name = ratingformat.name
        if ratingformat.iterable:
            cgi_rating[name] = {}
            for value in ratingformat.values:
                cgi_rating[name][value] = (value == 'none')
        else:
            cgi_rating[name] = ""

def _calc_ratings_display ():
    """Calculate current set of ratings to display."""
    global ratings_display, rating_modified
    urls = rating_store.keys()
    ratings_display = urls[curindex:curindex+_entries_per_page]
    rating_modified.clear()
    for _url in ratings_display:
        t = _strtime(rating_store[_url].modified)
        rating_modified[_url] = t.replace(u" ", u"&nbsp;")

_reset_cgi_rating()
_calc_ratings_display()


def _exec_form (form, lang):
    """HTML CGI form handling."""
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
    """Reset form variables to default values."""
    for key in info.keys():
        info[key] = False
    for key in error.keys():
        error[key] = False
    _reset_cgi_rating()
    global url, generic, curindex
    url = u""
    generic = False
    curindex = 0


def _form_url (form):
    """Check url validity."""
    global url
    if form.has_key('url'):
        val = _getval(form, 'url')
        url = _make_safe_url(val)
    return True


def _form_generic (form):
    """Check generic validity."""
    global generic
    generic = form.has_key('generic')
    return True


def _form_ratings (form):
    """Check rating value validity."""
    for name, value in _get_prefix_vals(form, 'rating_'):
        ratingformat = ratingservice.get_ratingformat(name)
        if ratingformat is None:
            # unknown rating
            error['ratingvalue'] = True
            return False
        if ratingformat.iterable:
            realvalue = value
        else:
            realvalue = _parse_range(value)
        if realvalue is None or not ratingformat.valid_value(realvalue):
            error['ratingvalue'] = True
            return False
        if ratingformat.iterable:
            for x in ratingformat.values:
                x = str(x)
                cgi_rating[name][x] = (value == x)
        else:
            cgi_rating[name] = value
        rating[name] = realvalue
    return True


def _form_selindex (index):
    """Display entries from given index."""
    global curindex
    try:
        curindex = int(index)
    except ValueError:
        error['selindex'] = True


def _calc_selindex (index):
    """Calculate ratings selection index."""
    global selindex
    res = [index-1000, index-250, index-50, index, index+50,
           index+250, index+1000]
    selindex = [ x for x in res if 0 <= x < len(rating_store) and x!=index ]


def _form_apply ():
    """Store changed ratings."""
    rating_store[url] = _WcUrlRating(url, rating, generic=generic)
    try:
        rating_store.write()
        info['ratingupdated'] = True
    except:
        error['ratingupdated'] = True


def _form_delete ():
    """Delete rating."""
    global url
    try:
        del rating_store[url]
        rating_store.write()
        info['ratingdeleted'] = True
    except:
        error['ratingdeleted'] = True


def _form_load ():
    """Load ratings."""
    global generic, url
    if url in rating_store:
        url_rating = rating_store[url]
        generic = url_rating.generic
        for name, value in url_rating.rating.iteritems():
            ratingformat = ratingservice.get_ratingformat(name)
            if ratingformat.iterable:
                for x in ratingformat.values:
                    cgi_rating[name][x] = x == value
            else:
                cgi_rating[name] = str(value)
