# -*- coding: iso-8859-1 -*-
"""filter according to rating rules"""
# Copyright (C) 2004  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from UrlRule import UrlRule
from wc import i18n
from wc.XmlUtils import xmlify, unxmlify

class RatingRule (UrlRule):
    """holds configured rating data"""
    def __init__ (self, sid=None, title="No title", desc="", disable=0):
        super(RatingRule, self).__init__(sid=sid, title=title,
                                        desc=desc, disable=disable)
        # category -> rating value
        self.ratings = {}
        self.url = ""


    def fill_attrs (self, attrs, name):
        if name=='category':
            assert self._service
            self._category = unxmlify(attrs.get('name')).encode('iso8859-1')
        elif name=='url':
            pass
        elif name=='rating':
            UrlRule.fill_attrs(self, attrs, name)
        else:
            raise ValueError(
    i18n._("Invalid rating rule tag name %r, check your configuration")%name)


    def fill_data (self, data, name):
        if name=='category':
            assert self._category
            if self._category not in self.ratings:
                self.ratings[self._category] = ""
            self.ratings[self._category] += data
        elif name=='url':
            self.url += data
        else:
            # ignore other content
            pass


    def compile_data (self):
        super(RatingRule, self).compile_data()
        self.url = unxmlify(self.url).encode('iso8859-1')
        for category, val in self.ratings.items():
            val = unxmlify(val).encode('iso8859-1')
            self.ratings[category] = val


    def fromFactory (self, factory):
        return factory.fromRatingRule(self)


    def toxml (self):
	s = "%s>\n" % super(RatingRule, self).toxml()
        if self.url:
            s += "<url>%s</url>\n" % xmlify(self.url)
        for category, value in self.ratings.items():
            s += "<category name=\"%s\">%s</category>\n"% \
                  (xmlify(category), xmlify(value))
        return s+"</rating>"

