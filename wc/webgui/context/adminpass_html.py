# -*- coding: iso-8859-1 -*-
from wc import AppName, Version, ConfigDir, config
from os.path import join as _join
from whrandom import choice as _choice
import string as _string

ConfigFile = _join(ConfigDir, "webcleaner.conf")
_chars = _string.letters + _string.digits
adminpass = ''.join([_choice(_chars) for i in range(8)])
adminuser = config['adminuser']
adminpass_b64 = adminpass.encode("base64").strip()

