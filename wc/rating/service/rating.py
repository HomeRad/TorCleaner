# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2009 Bastian Kleineidam
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
Rating import and export to various formats.
"""

from .. import Rating


def rating_from_headers (headers):
    """
    Parse X-Rating-* HTTP headers into a rating dictionary.
    @param headers: server headers
    @ptype headers: wc.http.header.WcMessage
    @return: parsed rating
    @rtype: wc.rating.Rating
    """
    rating = Rating()
    for name, value in headers:
        if name.lower().startswith("x-rating-"):
            rating[name[9:]] = value
    return rating
