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

import wc.rating
import wc.rating.service.ratingformat

class WebCleanerService (wc.rating.RatingService):
    """
    WebCleaner rating service supporting some basic categories:
    violence, sex, language, age.
    """

    def __init__ (self):
        """
        Initialize service data and a submit and request CGI url.
        """
        # service name
        self.name = "%s rating service" % wc.AppName
        # service homepage
        self.url = '%s/rating/' % wc.Url,
        # rating categories
        self.formats = [
            wc.rating.service.ratingformat.ValueFormat("violence"),
            wc.rating.service.ratingformat.ValueFormat("sex"),
            wc.rating.service.ratingformat.ValueFormat("language"),
            wc.rating.service.ratingformat.RangeFormat("age", minval=0),
        ]
        # submit ratings to service
        self.submit = '%s/submit' % self.url,
        # request ratings from service
        self.request = '%s/request' % self.url,
        self.cache = {}

    def get_url_rating (self, url):
        """
        Get rating for given url.
        """
        self.check_url(url)
        # use a specialized form of longest prefix matching:
        # split the url in parts and the longest matching part wins
        parts = wc.rating.split_url(url)
        # the range selects from all parts (full url) down to the first two parts
        for i in range(len(parts), 1, -1):
            url = "".join(parts[:i])
            if url in self.cache:
                return self.cache[url]
        raise KeyError(url)
