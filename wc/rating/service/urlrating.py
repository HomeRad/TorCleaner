# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2008 Bastian Kleineidam
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
import wc.rating

import time


class WcUrlRating (wc.rating.UrlRating):

    def __init__ (self, url, rating, generic=False, comment=None):
        super(WcUrlRating, self).__init__(url, rating, generic=generic)
        self.comment = comment
        self.modified = time.time()

    def __str__ (self):
        lines = []
        if self.generic:
            extra = " (generic)"
        else:
            extra = ""
        lines.append("<Rating for %s%s" % (self.url, extra))
        for item in self.rating.items():
            lines.append(" %s=%s" % item)
        lines.append(" comment=%s" % self.comment)
        return "\n".join(lines)
