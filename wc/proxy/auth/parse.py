# -*- coding: iso-8859-1 -*-
# Copyright (C) 2001-2006 Bastian Kleineidam
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
Parse basic and digest HTTP auth strings into key/value tokens.
"""

import wc.log

separators = ("()<>@,;:\\\"/[]?={} \t")
token_chars = ('!#$%&\'*+-.abcdefghijklmnopqrstuvwxyz'
               'ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`0123456789|~')

def parse_token (s, tok="", relax=False, more_chars=""):
    """
    Parse a token of data s, return tuple (tok, remaining data).
    If tok is empty, parse a default token.
    """
    if tok:
        if not s.startswith(tok):
            wc.log.warn(wc.LOG_AUTH, "expected %r start with %r", s, tok)
        if not relax:
            s = s[len(tok):]
    else:
        for i, c in enumerate(s):
            if c not in token_chars and c not in more_chars:
                i -= 1
                break
            tok += c
        s = s[i+1:]
    return tok, s.strip()


def parse_quotedstring (s):
    """
    Parse a quoted string token of s.

    @return: tuple (quoted, remaining data)
    """
    dummy, s = parse_token(s, tok='"')
    quoted = ""
    esc = False
    for i, c in enumerate(s):
        if esc:
            esc = False
        elif c == "\\":
            esc = True
            continue
        elif c == '"':
            break
        elif 31 < ord(c) < 127:
            quoted += c
    s = s[i:]
    dummy, s = parse_token(s, tok='"')
    return quoted, s.strip()


def parse_auth (auth, data):
    """
    Generic authentication tokenizer

    @param auth: default dictionary
    @param data: string data to parse
    @return: augmented auth dict and unparsed data
    """
    assert None == wc.log.debug(wc.LOG_AUTH, "parse authentication %r", data)
    while data:
        key, data = parse_token(data)
        if not data.startswith("="):
            data = "%s %s" % (key, data)
            break
        dummy, data = parse_token(data, tok="=")
        if data.startswith('"'):
            value, data = parse_quotedstring(data)
        else:
            value, data = parse_token(data)
        auth[key] = value
        if data:
            dummy, data = parse_token(data, tok=",")
    return auth, data.strip()
