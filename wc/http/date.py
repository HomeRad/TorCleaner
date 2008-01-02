# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2008 Bastian Kleineidam
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
HTTP date handling
"""

import locale
import time


# C locale weekday and month names
wkdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekdayname = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
               'Friday', 'Saturday', 'Sunday']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def get_date_rfc1123 (timesecs):
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
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % \
        (wkdayname[wd], day, monthname[month], year, hh, mm, ss)

def parse_date_rfc1123 (datestring):
    """
    """
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    t = time.strptime(datestring, "%a, %d %b %Y %H:%M:%S %Z")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t

def get_date_rfc850 (timesecs):
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
    return "%s, %02d-%s-%02d %02d:%02d:%02d GMT" % \
        (weekdayname[wd], day, monthname[month], year % 100, hh, mm, ss)

def parse_date_rfc850 (datestring):
    """
    """
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    t = time.strptime(datestring, "%A, %d-%b-%y %H:%M:%S %Z")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t

def get_date_asctime (timesecs):
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

def parse_date_asctime (datestring):
    """
    """
    # default to GMT timezone
    datestring += " GMT"
    curlocale = locale.getlocale(locale.LC_TIME)
    locale.setlocale(locale.LC_TIME, 'C')
    try:
        t = time.strptime(datestring, "%a %b %d %H:%M:%S %Y %Z")
    except ValueError:
        t = time.strptime(datestring, "%a %b  %d %H:%M:%S %Y %Z")
    locale.setlocale(locale.LC_TIME, curlocale)
    return t


def parse_http_date (datestring):
    """
    Try to parse HTTP-date.
    @return: the parsed date or None on error
    @rtype: time.struct_time or None
    """
    try:
        return parse_date_rfc1123(datestring)
    except ValueError:
        pass
    try:
        return parse_date_rfc850(datestring)
    except ValueError:
        pass
    try:
        return parse_date_asctime(datestring)
    except ValueError:
        pass
    return None
