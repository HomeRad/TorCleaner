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
Rating data storage.
"""

import wc.url
import wc.filter.rating

class Storage (object):
    """
    Basic storage class for ratings.
    """

    def __setitem__ (self, url, rating):
        """
        Add rating for given url.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def __delitem__ (self, url):
        """
        Remove rating for given url.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def __getitem__ (self, url):
        """
        Get rating for given url.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def __iter__ (self):
        """
        Iterate over stored urls.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def keys (self):
        """
        Return list of urls for whom ratings are stored.
        """
        return [x for x in self]

    def __len__ (self):
        """
        Number of stored ratings.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def __contains__ (self, url):
        """
        True if rating for given url is stored.
        """
        raise NotImplementedError, "must be implemented in subclass"

    def check_url (self, url):
        """
        If url is not safe raise a RatingParseError.
        """
        if not wc.url.is_safe_url(url):
            raise wc.filter.rating.RatingParseError, \
                                  "Invalid rating url %s." % repr(url)

    def load (self):
        """
        Load stored data into this instance.
        """
        pass

    def write (self):
        """
        Write data of this instance.
        """
        pass


# mapping {class name -> storage class instance}
_stored = {}
def get_rating_store (klass):
    """
    Get instance of rating store klass or create a new one.
    """
    name = klass.__name__
    if name not in _stored:
        _stored[name] = klass()
    return _stored[name]
