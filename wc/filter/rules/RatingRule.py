# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
import wc.rating
from wc.rating.service import ratingservice
#import wc.rating.storage


MISSING = _("Unknown page")


class RatingRule (wc.filter.rules.UrlRule.UrlRule):
    """
    Holds a rating to match against when checking for allowance of
    the rating system.
    Also stored is the url to display should a rating deny a page.
    The use_extern flag determines if the filters should parse and use
    external rating data from HTTP headers or HTML <meta> tags.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None, disable=0,
                  matchurls=None, nomatchurls=None, use_extern=0):
        """Initialize rating data."""
        super(RatingRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.rating = wc.rating.Rating()
        self.url = ""
        self.use_extern = use_extern
        self.attrnames.append('use_extern')
        self.intattrs.append('use_extern')

    def fill_attrs (self, attrs, name):
        """Init rating and url attrs."""
        super(RatingRule, self).fill_attrs(attrs, name)
        if name == 'limit':
            self._name = attrs.get('name')

    def end_data (self, name):
        """Store category or url data."""
        super(RatingRule, self).end_data(name)
        if name == 'limit':
            self.rating[self._name] = self._data
        elif name == 'url':
            self.url = self._data

    def compile_data (self):
        """Compile parsed rule values."""
        super(RatingRule, self).compile_data()
        self.compile_values()

    def compile_values (self):
        """Fill missing rating values."""
        # helper dict for web gui
        self.values = {}
        for ratingformat in ratingservice.ratingformats:
            name = ratingformat.name
            self.values[name] = {}
            if name not in self.rating:
                # Use the most restrictive setting as default.
                value = ratingformat.values[0]
                self.rating[name] = value
            if ratingformat.iterable:
                for value in ratingformat.values:
                    value = str(value)
                    self.values[name][value] = value == self.rating[name]

    def toxml (self):
        """Rule data as XML for storing."""
        s = u'%s\n use_extern="%d">' % (super(RatingRule, self).toxml(),
                                        self.use_extern)
        s += u"\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.url:
            s += u"\n  <url>%s</url>" % wc.XmlUtils.xmlquote(self.url)
        for name, value in self.rating.iteritems():
            value = wc.XmlUtils.xmlquote(str(value))
            name = wc.XmlUtils.xmlquoteattr(name)
            s += u"\n  <limit name=\"%s\">%s</limit>" % (name, value)
        s += u"\n</%s>" % self.name
        return s
