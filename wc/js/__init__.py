"""JavaScript helper classes and a Spidermonkey wrapper module"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003  Bastian Kleineidam
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

import re

def escape_js (script):
    script = script.replace('--', '-&#45;')
    script = re.sub(r'(?i)</script>', '&#60;/script>', script)
    return script


def unescape_js (script):
    script = script.replace('-&#45;', '--')
    script = script.replace('&#60;/script>', '</script>')
    return script


def get_js_data (attrs):
    """get js_ok flag and js_lang from given attrs"""
    js_lang = attrs.get('language', '').lower()
    js_type = attrs.get('type', '').lower()
    js_ok = js_type=='text/javascript' or \
            js_type.startswith('javascript') or \
            js_lang.startswith('javascript') or \
            not (js_lang or js_type)
    return js_ok, js_lang


has_js_ver = re.compile(r'(?i)javascript(?P<num>\d\.\d)').search
def get_js_ver (language):
    """get js version as float"""
    ver = 0.0
    if language:
        mo = has_js_ver(language)
        if mo:
            ver = float(mo.group('num'))
    return ver
