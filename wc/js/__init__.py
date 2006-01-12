# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2006 Bastian Kleineidam
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
    script = remove_html_comments(script)
    if not jscomments:
        script = remove_js_comments(script)
    return u"\n<!--\n%s\n//-->\n" % script


def remove_whitespace (script):
    lines = []
    for line in script.splitlines():
        line = line.rstrip()
        if line:
            lines.append(line)
    return "\n".join(lines)


_start_js_comment = re.compile(r"^<!--([^\r\n]+)?").search
_end_js_comment = re.compile(r"\s*(?P<comment>//)?[^/\r\n]*-->[ \t]*$").search
def remove_html_comments (script):
    """
    Remove leading and trailing HTML comments from the script text.
    """
    script = remove_whitespace(script)
    mo = _start_js_comment(script)
    if mo:
        script = script[mo.end():]
    mo = _end_js_comment(script)
    if mo:
        if mo.group("comment") is not None:
            i = script.rindex("//")
        else:
            i = script.rindex("-->")
        script = script[:i]
    return script.strip()


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
    """
    Get js version as float.
    """
    ver = 0.0
    if language:
        mo = has_js_ver(language)
        if mo:
            ver = float(mo.group('num'))
    return ver


def is_safe_js_url (source_url, target_url):
    """
    Test validity of a background JS download.
    """
    source = wc.url.url_split(source_url)
    target = wc.url.url_split(target_url)
    if target[0] and target[0].lower() not in ('http', 'https'):
        return False
    # no redirects from external to local host
    localhosts = wc.dns.resolver.get_default_resolver().localhosts
    if source[1] not in localhosts and \
       target[1] in localhosts:
        return False
    return True

