# -*- coding: iso-8859-1 -*-
from wc import AppName, Version, ConfigDir, config
from wc.webgui.context import getval as _getval
import cgi as _cgi

url = ""

# form execution
def _exec_form (form):
    global url
    if form.has_key('url'):
        url = _getval(form, 'url')
