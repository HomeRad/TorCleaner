# -*- coding: iso-8859-1 -*-
"""parameters for blocked.html page"""
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

from wc import AppName, Version
from wc.webgui.context import getval as _getval

rule = None
selfolder = 0
selrule = 0

# form execution
def _exec_form (form, lang):
    global rule, selfolder, selrule
    if form.has_key('rule'):
        rule = _getval(form, 'rule')
    if form.has_key('selfolder'):
        selfolder = int(_getval(form, 'selfolder'))
    if form.has_key('selrule'):
        selrule = int(_getval(form, 'selrule'))

