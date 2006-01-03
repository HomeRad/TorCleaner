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
Services.
"""

import wc
import wc.filter.rating.category


class Service (object):
    """
    A named service with url and list of supported categories.
    """

    def __init__ (self, name, url, categories):
        """
        Initialize name, url and category list.
        """
        self.name = name
        self.url = url
        self.categories = categories

    def __cmp__ (self, other):
        """
        Compare two service objects by name.
        """
        return cmp(self.name, other.name)

    def __str__ (self):
        return "Service %r (%r)" % (self.name, self.url)


class WebCleanerService (Service):
    """
    WebCleaner rating service supporting some basic categories:
    violence, sex, language, age.
    """

    def __init__ (self):
        """
        Initialize service data and a submit and request CGI url.
        """
        # service name
        name = wc.AppName
        # service homepage
        url = '%s/rating/' % wc.Url,
        # rating categories
        categories = [
            wc.filter.rating.category.ValueCategory("violence"),
            wc.filter.rating.category.ValueCategory("sex"),
            wc.filter.rating.category.ValueCategory("language"),
            wc.filter.rating.category.RangeCategory("age", minval=0),
        ]
        super(WebCleanerService, self).__init__(name, url, categories)
        # submit ratings to service
        self.submit = '%s/submit' % self.url,
        # request ratings from service
        self.request = '%s/request' % self.url,
