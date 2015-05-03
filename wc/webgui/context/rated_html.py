# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Parameters for rated.html page.
"""

from wc import AppName, Version
from wc.configuration import config
from wc.webgui.context import getval as _getval
from wc.configuration.ratingstorage import make_safe_url as _make_safe_url

url = None
safeurl = None
reason = None

def _form_reset():
    global url, reason
    url = u""
    safeurl = u""
    reason = _("Unknown reason")


# form execution
def _exec_form(form, lang):
    """
    HTML CGI form handling.
    """
    global url, safeurl, reason
    if 'url' in form:
        url = _getval(form, 'url')
        safeurl = _make_safe_url(url)
    if 'reason' in form:
        reason = _getval(form, 'reason')
