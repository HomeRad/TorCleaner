# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
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
