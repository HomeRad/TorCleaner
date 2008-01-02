# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2008 Bastian Kleineidam
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
JavaScript helper classes and a Spidermonkey wrapper module.
"""

import re
import wc.dns
import wc.url


def clean (script, jscomments=True):
    """
    Clean script from comments and HTML.
    """
    script = escape_js(remove_html_comments(script, jscomments=jscomments))
    return u"//<![CDATA[\n%s//]]>" % script


script_sub = re.compile(r"(?i)</script\s*>").sub
def escape_js (script):
    """
    Escape HTML stuff in JS script.
    """
    lines = []
    for line in script.splitlines():
        line = line.rstrip()
        lines.append(escape_js_line(line))
    return "\n".join(lines)


def escape_js_line (script):
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
            if script[i:i+9].lower() == '</script>':
                if quote:
                    script = script[:i] + "</scr" + quote + "+" + \
                             quote + "ipt>" + script[(i+9):]
                else:
                    script = script[:i] + script[(i+9):]
            escape = False
        else:
            escape = False
        i += 1
    #script = script.replace('-->', '--&#62;')
    #script = script_sub("&#60;/script&#62;", script)
    return script


_start_js_comment = re.compile(r"^(<!--|//<!\[CDATA\[)").search
_end_js_comment = re.compile(r"""\s*
    (?P<lcomment>//[^/]*)? # leading comment
    (?P<ecomment>--> | \]\]>) # ending comment
    $""", re.VERBOSE).search
def remove_html_comments (script, jscomments=True):
    """
    Remove leading and trailing HTML comments from the script text.
    And remove JS comments if flag is not set.
    """
    lines = []
    for line in script.splitlines():
        line = line.rstrip()
        if line and (jscomments or not line.lstrip().startswith('//')):
            lines.append(line)
    if not lines:
        return ""
    mo = _start_js_comment(lines[0])
    if mo:
        del lines[0]
    if not lines:
        return ""
    mo = _end_js_comment(lines[-1])
    if mo:
        if mo.group("lcomment") is not None:
            # cut at leading comment
            i = mo.start("lcomment")
        else:
            # cut at ending comment
            i = mo.start("ecomment")
        lines[-1] = lines[-1][:i]
    return "\n".join(lines)


def remove_js_comments (script):
    """
    XXX use spidermonkey scanner here
    """
    res = []
    for line in script.splitlines():
        if not line.lstrip().startswith('//'):
            res.append(line)
    return "\n".join(res)


def get_js_data (attrs):
    """
    Get js_ok flag and js_lang from given attrs.
    """
    js_lang = attrs.get_true('language', '').lower()
    js_type = attrs.get_true('type', '').lower()
    js_ok = js_type == 'text/javascript' or \
            js_type.startswith('javascript') or \
            js_lang.startswith('javascript') or \
            not (js_lang or js_type)
    return js_ok, js_lang


has_js_ver = re.compile(r'(?i)javascript(?P<num>\d\.\d)').search
def get_js_ver (language):
    """Get js version as float."""
    ver = 0.0
    if language:
        mo = has_js_ver(language)
        if mo:
            ver = float(mo.group('num'))
    return ver


def is_safe_js_url (source_url, target_url):
    """Test validity of a background JS download."""
    source = wc.url.url_split(source_url)
    target = wc.url.url_split(target_url)
    if target[0] and target[0].lower() not in ('http', 'https'):
        return False
    if not target[1]:
        return False
    # no redirects from external to local host
    localhosts = wc.dns.resolver.get_default_resolver().localhosts
    if source[1] not in localhosts and \
       target[1] in localhosts:
        return False
    return True
