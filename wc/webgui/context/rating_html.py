# -*- coding: iso-8859-1 -*-
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

from wc import AppName, Version, ConfigDir, config
from wc.webgui.context import getval as _getval
from wc.filter.Rating import service, rangenames
_entries_per_page = 50

# config vars
info = {}
error = {}
ratings = {}
values = {}
url = ""
# current index of entry to display
curindex = 0
entries_display = []

# form execution
def _exec_form (form):
    # reset info/error and form vals
    _form_reset()
    global url
    if form.has_key('url'):
        url = _getval(form, 'url')

def _form_reset ():
    info.clear()
    error.clear()
    ratings.clear()
    global url, curindex
    url = ""
    curindex = 0
