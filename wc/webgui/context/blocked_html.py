# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
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

def _exec_form(form, lang):
    """
    HTML CGI form handling.
    """
    global ruletitle, selfolder, selrule
    if 'ruletitle' in form:
        ruletitle = _getval(form, 'ruletitle')
    if 'selfolder' in form:
        selfolder = int(_getval(form, 'selfolder'))
    if 'selrule' in form:
        selrule = int(_getval(form, 'selrule'))
    if 'blockurl' in form:
        _handle_blockurl(_getval(form, 'blockurl'))


def _handle_blockurl(url):
    global blocked_url, blocked_url_nofilter, blocked_host
    blocked_url = url
    parts = list(_url_split(url))
    blocked_host = "%s:%d" % (parts[1], parts[2])
    parts[1] += ".wc-nofilter-blocker"
    blocked_url_nofilter = _url_unsplit(parts)
