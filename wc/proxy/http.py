# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

is_http_status = re.compile(r'^\d\d\d$').search
def parse_http_response (response, url):
    """
    Parse a HTTP response status line into tokens.

    @return: (version, status, msg)
    @rtype: ((int, int), int, string)
    """
    parts = response.split(None, 2)
    if len(parts) == 2:
        wc.log.warn(wc.LOG_PROXY, "empty response message from %r", url)
        parts += ['Bummer']
    elif len(parts) != 3:
        wc.log.warn(wc.LOG_PROXY, "invalid response %r from %r",
                    response, url)
        parts = ['HTTP/1.0', "200", 'Ok']
    if not is_http_status(parts[1]):
        wc.log.warn(wc.LOG_PROXY, "invalid http statuscode %r from %r",
                    parts[1], url)
        parts[1] = "200"
    parts[1] = int(parts[1])
    version = parts[0][5:]
    parts[0] = parse_http_version(parts[0])
    return parts


def parse_http_version (version):
    # set to invalid version
    res = (2,0)
    if version.lower().startswith("http/") and "." in version:
        major, minor = version[5:].split(".", 1)
        try:
            major = int(major)
            minor = int(minor)
            if major >= 0 and minor >= 0:
                res = (major, minor)
        except (ValueError, OverflowError):
            pass
    return res

