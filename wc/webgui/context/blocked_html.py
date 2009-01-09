# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
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
Parameters for blocked.html page.
"""

from wc import AppName, Version
from wc.url import url_split as _url_split
from wc.url import url_unsplit as _url_unsplit
from wc.webgui.context import getval as _getval

ruletitle = None
selfolder = 0
selrule = 0
blocked_url = "http://imadoofus.org/"
blocked_url_nofilter = "http://imadoofus.org.wc-nofilter/"
blocked_host = "imadoofus.org"

def _exec_form (form, lang):
    """
    HTML CGI form handling.
    """
    global ruletitle, selfolder, selrule
    if form.has_key('ruletitle'):
        ruletitle = _getval(form, 'ruletitle')
    if form.has_key('selfolder'):
        selfolder = int(_getval(form, 'selfolder'))
    if form.has_key('selrule'):
        selrule = int(_getval(form, 'selrule'))
    if form.has_key('blockurl'):
        _handle_blockurl(_getval(form, 'blockurl'))


def _handle_blockurl (url):
    global blocked_url, blocked_url_nofilter, blocked_host
    blocked_url = url
    parts = list(_url_split(url))
    blocked_host = "%s:%d" % (parts[1], parts[2])
    parts[1] += ".wc-nofilter-blocker"
    blocked_url_nofilter = _url_unsplit(parts)
