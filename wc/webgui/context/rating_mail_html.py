# -*- coding: iso-8859-1 -*-
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

from wc import AppName, Email, Version, ConfigDir, config
from wc.webgui.context import getval as _getval
from wc.filter.Rating import rating_cache_get as _rating_cache_get
from wc.filter.Rating import rating_export as _rating_export
from wc.url import is_valid_url as _is_valid_url

info = {}
error = {}
url = ""
rating = ""


# form execution
def _exec_form (form, lang):
    # reset info/error and form vals
    _form_reset()
    # calculate global vars
    if not _form_url(form):
        return
    if not _get_rating():
        return
    if form.has_key('send'):
        _form_send()


def _form_reset ():
    info.clear()
    error.clear()
    global url, rating
    url = ""
    rating = ""


def _form_url (form):
    global url, rating
    if form.has_key('url'):
        val = _getval(form, 'url')
        if not _is_valid_url(val):
            error['url'] = True
            return False
        url = val
    return True


def _get_rating ():
    if not url:
        error["url"] = True
        return False
    val = _rating_cache_get(url)
    if val is None:
        error["rating"] = True
        return False
    global rating
    rating = "url %r\n%s\n"%(url, _rating_export(val[1]))


def _form_send ():
    XXX
    info["sent"] = True
