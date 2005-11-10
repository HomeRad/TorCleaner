# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Filter according to rating rules.
"""

import wc
import wc.log
import wc.filter.rules.UrlRule
import wc.XmlUtils
import wc.filter.rating
import wc.filter.rating.storage


MISSING = _("Unknown page")


class RatingRule (wc.filter.rules.UrlRule.UrlRule):
    """
    Holds configured rating data.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None, disable=0,
                  matchurls=None, nomatchurls=None):
        """
        Call super.__init__(), store ratings in a mapping, initialize url.
        Rating mapping has the form {category name -> limit}.
        """
        super(RatingRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.ratings = {}
        for category in wc.filter.rating.categories:
            if category.iterable:
                self.ratings[category.name] = 'none'
            else:
                self.ratings[category.name] = ""
        self.url = ""

    def fill_attrs (self, attrs, name):
        """
        Init rating and url attrs.
        """
        super(RatingRule, self).fill_attrs(attrs, name)
        if name == 'category':
            self._category = attrs.get('name')

    def end_data (self, name):
        """
        Store category or url data.
        """
        super(RatingRule, self).end_data(name)
        if name == 'category':
            assert self.ratings.has_key(self._category), repr(self._category)
            self.ratings[self._category] = self._data
        elif name == 'url':
            self.url = self._data

    def compile_data (self):
        """
        Call super.compile_data() and compile_values().
        """
        super(RatingRule, self).compile_data()
        self.compile_values()

    def compile_values (self):
        """
        Fill rating values mapping of the form
        {category name -> value -> value_is_set}
        with types
        {string -> string -> bool}
        """
        self.values = {}
        for name, value in self.ratings.items():
            category = wc.filter.rating.get_category(name)
            if category.iterable:
                self.values[name] = {}
                for v in category.values:
                    self.values[name][v] = (v == value)
            else:
                self.values[name] = value

    def rating_allow (self, url):
        """
        Asks cache if the rule allows the rating data for given url
        Looks up cache to find rating data, if not returns a MISSING message.
        """
        rating_store = wc.filter.rating.get_ratings()
        # sanitize url
        url = wc.filter.rating.make_safe_url(url)
        if url in rating_store:
            return self.check_against(rating_store[url])
        return MISSING

    def check_against (self, rating):
        """
        Return None if allowed, else a reason of why not.
        """
        for catname, value in rating.category_values.items():
            if catname not in self.ratings:
                wc.log.warn(wc.LOG_FILTER,
                            "Unknown rating category %r specified", catname)
                continue
            if not value:
                # empty value implicates not rated
                continue
            limit = self.ratings[catname]
            if not limit:
                # no limit is set for this category
                continue
            category = wc.filter.rating.get_category(catname)
            reason = category.allowance(value, limit)
            if reason:
                return reason
        # not exceeded
        return None

    def toxml (self):
        """
        Rule data as XML for storing.
        """
        s = u"%s>" % super(RatingRule, self).toxml()
        s += u"\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.url:
            s += u"\n  <url>%s</url>" % wc.XmlUtils.xmlquote(self.url)
        for category, value in self.ratings.items():
            if value is not None:
                s += u"\n  <category name=\"%s\">%s</category>" % \
                      (wc.XmlUtils.xmlquoteattr(category),
                       wc.XmlUtils.xmlquote(value))
        s += u"\n</%s>" % self.get_name()
        return s
