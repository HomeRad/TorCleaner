# -*- coding: iso-8859-1 -*-
"""parameters for update_doit.html page"""
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

from wc import AppName, Version, config, i18n
from wc.update import update_filter as _update_filter
from wc.update import update_ratings as _update_ratings
from cStringIO import StringIO as _StringIO

updatelog = ""

def _exec_form (form, lang):
    if form.has_key('updatezapper'):
        _updatezapper()
    elif form.has_key('updaterating'):
        _updaterating()
    else:
        global updatelog
        updatelog = i18n._("Error: nothing to update.")


def _updatezapper ():
    global updatelog
    log = _StringIO()
    doreload = False
    try:
        doreload = _update_filter(config, log=log, dryrun=False)
        updatelog = log.getvalue()
        config.write_filterconf()
    except IOError, msg:
        updatelog = "Error: %s" % msg
    else:
        if doreload:
            # pass
            pass


def _updaterating ():
    global updatelog
    log = _StringIO()
    try:
        # XXX
        _update_ratings(config, log=log, dryrun=False)
    except IOError, msg:
        updatelog = "Error: %s" % msg
