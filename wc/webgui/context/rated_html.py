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
Parameters for rated.html page.
"""

from wc import AppName, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval

url = None
reason = None

def _form_reset ():
    global url, reason
    url = u""
    reason = _("Unknown reason")


# form execution
def _exec_form (form, lang):
    global url, reason
    if form.has_key('url'):
        url = _getval(form, 'url')
    if form.has_key('reason'):
        reason = _getval(form, 'reason')
