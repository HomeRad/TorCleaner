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
from wc.XmlUtils import xmlify
from wc.filter.Rating import service, rating_in_range
from wc.log import *


class RatingRule (UrlRule):
    """holds configured rating data"""
    def __init__ (self, sid=None, titles=None, descriptions=None, disable=0):
        super(RatingRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        # category -> rating value
        self.ratings = {}
        self.url = ""


    def fill_attrs (self, attrs, name):
        """init rating and url attrs"""
        super(RatingRule, self).fill_attrs(attrs, name)
        if name=='category':
            self._category = attrs.get('name')


    def end_data (self, name):
        super(RatingRule, self).end_data(name)
        if name=='category':
            assert self._category
            self.ratings[self._category] = self._data
        elif name=='url':
            self.url = self._data


    def compile_data (self):
        """fill rating structure"""
        super(RatingRule, self).compile_data()
        for category, catdata in service['categories'].items():
            if category not in self.ratings:
                if catdata.has_key('rvalues'):
                    self.ratings[category] = catdata['rvalues'][0]
                else:
                    self.ratings[category] = ""
        self.compile_values()


    def compile_values (self):
        """initialize rating data"""
        self.values = {}
        for category, val in self.ratings.items():
            if val:
                self.values[category] = {val:True}


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromRatingRule(self)


    def check_against (self, rating):
        """rating is a mapping category -> value
           return None if allowed, else a reason of why not"""
        for category, value in rating.items():
            if category not in self.ratings:
                warn(FILTER, "Unknown rating category %r specified", category)
                continue
            if not value:
                # empty value implicates not rated
                continue
            limit = self.ratings[category]
            if not limit:
                # no limit is set for this category
                continue
            elif service['categories'][category].has_key('rrange'):
                # check if value is in range
                if (limit[0] is not None and value < limit[0]) or \
                   (limit[1] is not None and value > limit[1]):
                    return i18n._("Rating %r for category %r is not in range %s") %\
                                  (value, category, limit)
            elif value > limit:
                return i18n._("Rating %r for category %r exceeds limit %r")%\
                              (value, category, limit)
        # not exceeded
        return None


    def toxml (self):
        """Rule data as XML for storing"""
	s = "%s>" % super(RatingRule, self).toxml()
        s += "\n"+self.title_desc_toxml(prefix="  ")
        if self.matchurls or self.nomatchurls:
            s += "\n"+self.matchestoxml(prefix="  ")
        if self.url:
            s += "\n  <url>%s</url>" % xmlify(self.url)
        for category, value in self.ratings.items():
            if value:
                s += "\n  <category name=\"%s\">%s</category>"% \
                      (xmlify(category), xmlify(value))
        s += "\n</%s>" % self.get_name()
        return s

