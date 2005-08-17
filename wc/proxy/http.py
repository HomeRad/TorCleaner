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
import wc
import wc.log

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
    res = (2,0)
    if version.startswith("HTTP/") and "." in version:
        major, minor = version[5:].split(".", 1)
        try:
            major = int(major)
            minor = int(minor)
            if major >= 0 and minor >= 0:
                res = (major, minor)
        except (ValueError, OverflowError):
            pass
    return res


# C locale weekday and month names
wkdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekdayname = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
               'Friday', 'Saturday', 'Sunday']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def get_date_rfc1123 (self, timesecs):
    """
    RFC 822, updated by RFC 1123
    Grammar:
    rfc1123-date = wkday "," SP date1 SP time SP "GMT"
    date1        = 2DIGIT SP month SP 4DIGIT
                   ; day month year (e.g., 02 Jun 1982)
    time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT
                   ; 00:00:00 - 23:59:59
    wkday        = "Mon" | "Tue" | "Wed"
                 | "Thu" | "Fri" | "Sat" | "Sun"
    month        = "Jan" | "Feb" | "Mar" | "Apr"
                 | "May" | "Jun" | "Jul" | "Aug"
                 | "Sep" | "Oct" | "Nov" | "Dec"
    Example: Sun, 06 Nov 1994 08:49:37 GMT
    """
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timesecs)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % \
        (wkdayname[wd], day, monthname[month], year, hh, mm, ss)

def parse_date_rfc1123 (self, datestring):
    """
    """
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    t = time.strptime(datestring, "%a, %d %b %Y %H:%M:%S %Z")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t

def get_date_rfc850 (self, timesecs):
    """
    RFC 850, obsoleted by RFC 1036
    Grammar:
    rfc850-date  = weekday "," SP date2 SP time SP "GMT"
    date2        = 2DIGIT "-" month "-" 2DIGIT
                   ; day-month-year (e.g., 02-Jun-82)
    time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT
                   ; 00:00:00 - 23:59:59
    weekday      = "Monday" | "Tuesday" | "Wednesday"
                 | "Thursday" | "Friday" | "Saturday" | "Sunday"
    month        = "Jan" | "Feb" | "Mar" | "Apr"
                 | "May" | "Jun" | "Jul" | "Aug"
                 | "Sep" | "Oct" | "Nov" | "Dec"
    Example: Sunday, 06-Nov-94 08:49:37 GMT
    """
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timesecs)
    return "%s, %02d-%3s-%2d %02d:%02d:%02d GMT" % \
        (weekdayname[wd], day, monthname[month], year % 100, hh, mm, ss)

def parse_date_rfc850 (self, datestring):
    """
    """
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    t = time.strptime(datestring, "%A, %d-%b-%y %H:%M:%S %Z")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t

def get_date_asctime (self, timesecs):
    """
    ANSI C's asctime() format
    Grammar:
    asctime-date = wkday SP date3 SP time SP 4DIGIT
    date3        = month SP ( 2DIGIT | ( SP 1DIGIT ))
                   ; month day (e.g., Jun  2)
    time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT
                   ; 00:00:00 - 23:59:59
    wkday        = "Mon" | "Tue" | "Wed"
                 | "Thu" | "Fri" | "Sat" | "Sun"
    month        = "Jan" | "Feb" | "Mar" | "Apr"
                 | "May" | "Jun" | "Jul" | "Aug"
                 | "Sep" | "Oct" | "Nov" | "Dec"
    Example: Sun Nov  6 08:49:37 1994
    """
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timesecs)
    return "%s %3s %2d %02d:%02d:%02d %4d" % \
        (wkdayname[wd], monthname[month], day, hh, mm, ss, year)

def parse_date_asctime (self, datestring):
    """
    """
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    try:
        t = time.strptime(datestring, "%a %b %d %H:%M:%S %Y")
    except ValueError:
        t = time.strptime(datestring, "%a %b  %d %H:%M:%S %Y")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t
