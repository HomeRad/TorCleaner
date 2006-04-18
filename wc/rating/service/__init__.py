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

import wc
import wc.rating

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
        # rating formats
        import ratingformat
        self.ratingformats = [
            ratingformat.ValueFormat("WC-Violence"),
            ratingformat.ValueFormat("WC-Sex"),
            ratingformat.ValueFormat("WC-Language"),
            ratingformat.RangeFormat("WC-Age", minval=0),
        ]
        # submit ratings to service
        self.submit = '%s/submit' % self.url,
        # request ratings from service
        self.request = '%s/request' % self.url,
        self.cache = {}

    def get_ratingformat (self, name):
        name = name.lower()
        for format in self.ratingformats:
            if format.name.lower() == name:
                return format
        return None

# instantiate the global service
ratingservice = WebCleanerService()
