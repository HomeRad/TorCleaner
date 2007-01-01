# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2007 Bastian Kleineidam
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
Parameters for adminpass.html page.
"""

from wc import AppName, Version
from wc.configuration import config
from os.path import join as _join
from random import choice as _choice
import string as _string

ConfigFile = _join(config.configdir, "webcleaner.conf")
_chars = _string.letters + _string.digits
adminpass = u''.join([_choice(_chars) for i in xrange(8)])
adminuser = config.get('adminuser', u'admin')
adminpass_b64 = adminpass.encode("base64").strip()
