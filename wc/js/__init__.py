# -*- coding: iso-8859-1 -*-
"""JavaScript helper classes and a Spidermonkey wrapper module"""
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

import re


_start_js_comment = re.compile(r"^<!--([^\r\n]+)?").search
_end_js_comment = re.compile(r"\s*//[^\r\n]*-->[ \t]*$").search

def remove_html_comments (script):
    """remove leading and trailing HTML comments from the script text"""
    mo = _start_js_comment(script)
    if mo:
        script = script[mo.end():]
    mo = _end_js_comment(script)
    if mo:
        script = script[:mo.start()]
    return script.strip()


def escape_js (script):
    """escape HTML stuff in JS script"""
    # if we encounter "</script>" in the script, we assume that is
    # in a quoted string. The solution is to split it into
    # "</scr"+"ipt>" (with the proper quotes of course)
    quote = False
    escape = False
    i = 0
    while i < len(script):
        c = script[i]
        if c == '"' or c == "'":
            if not escape:
                if quote == c:
                    quote = False
                elif not quote:
                    quote = c
            escape = False
        elif c == '\\':
            escape = not escape
        elif c == '<':
            if script[i:i+9].lower() == '</script>' and quote:
                script = script[:i]+"</scr"+quote+"+"+quote+"ipt>"+\
                         script[(i+9):]
            escape = False
        else:
            escape = False
        i += 1
    script = script.replace('-->', '--&#62;')
    return script


def get_js_data (attrs):
    """get js_ok flag and js_lang from given attrs"""
    js_lang = attrs.get('language', '').lower()
    js_type = attrs.get('type', '').lower()
    js_ok = js_type == 'text/javascript' or \
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
