# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
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
HTTP related utility functions.
"""

import re
import BaseHTTPServer
from .. import log, LOG_PROXY
from .date import parse_http_date

responses = BaseHTTPServer.BaseHTTPRequestHandler.responses

def parse_http_request (request):
    """
    Parse a HTTP request line into tokens.

    @return: (method, url, version)
    @rtype: (string, string, (int, int))
    """
    method = ""
    url = ""
    version = (2, 0)
    parts = request.split()
    if len(parts) == 3:
        method = parts[0].upper()
        url = parts[1]
        version = parse_http_version(parts[2])
    return (method, url, version)


is_http_status = re.compile(r'^[1-5]\d\d$').search
def parse_http_response (response, url):
    """
    Parse a HTTP response status line into tokens.

    @return: (version, status, msg)
    @rtype: ((int, int), int, string)
    """
    parts = response.split(None, 2)
    if len(parts) == 2:
        parts += ['Bummer']
    elif len(parts) != 3:
        log.info(LOG_PROXY, "invalid response %r from %r", response, url)
        parts = ['HTTP/1.0', "200", 'OK']
    if not is_http_status(parts[1]):
        log.info(LOG_PROXY, "invalid http statuscode %r from %r",
            parts[1], url)
        parts[1] = "200"
    parts[1] = int(parts[1])
    if parts[1] in responses:
        # use canonical response message
        parts[2] = responses[parts[1]][0]
    version = parts[0].upper()
    parts[0] = parse_http_version(version)
    return parts


def parse_http_version (version):
    """
    Parse a HTTP version string.

    @return: (major, minor)
    @rtype: (int, int)
    """
    # set to invalid version
    res = (2, 0)
    if version.upper().startswith("HTTP/") and "." in version:
        major, minor = version[5:].split(".", 1)
        try:
            major = int(major)
            minor = int(minor)
            if major >= 0 and minor >= 0:
                res = (major, minor)
        except (ValueError, OverflowError):
            pass
    return res


def parse_http_warning (warning):
    """
    Grammar for a warning:
    Warning    = "Warning" ":" 1#warning-value
    warning-value = warn-code SP warn-agent SP warn-text [SP warn-date]
    warn-code  = 3DIGIT
    warn-agent = ( host [ ":" port ] ) | pseudonym
                    ; the name or pseudonym of the server adding
                    ; the Warning header, for use in debugging
    warn-text  = quoted-string
    warn-date  = <"> HTTP-date <">
    """
    try:
        warncode, warning = warning.split(None, 1)
        warncode = int(warncode)
        # support unquoted warnings (eg. '110 Response is stale')
        if '"' in warning:
            warnagent, warning = warning.split(None, 1)
            warntext, warning = split_quoted_string(warning)
        else:
            warnagent = ""
            warntext, warning = warning, None
        if warning:
            if warning.startswith('"'):
                warndate, warning = split_quoted_string(warning)
            else:
                warndate = warning
            warndate = parse_http_date(warndate)
        else:
            warndate = None
    except (ValueError, OverflowError):
        return None
    return warncode, warnagent, warntext, warndate


def split_quoted_string (s):
    """
    Split off a leading quoted string.
    """
    if not s.startswith('"'):
        raise ValueError("No quoted string found")
    quoted = ""
    i = 1
    escape = False
    while i < len(s):
        if s[i] == '\\' and not escape:
            escape = True
            i += 1
            continue
        if s[i] == '"' and not escape:
            break
        quoted += s[i]
        escape = False
        i += 1
    return (quoted, s[i+1:].lstrip())
