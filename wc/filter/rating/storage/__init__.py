# -*- coding: iso-8859-1 -*-
"""Storage."""
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

import wc.url
import wc.filter.rating

class Storage (object):
    """Storage for ratings."""

    def __setitem__ (self, url, rating):
        """Add rating for given url."""
        raise NotImplementedError, "must be implemented in subclass"

    def __delitem__ (self, url):
        """Remove rating for given url."""
        raise NotImplementedError, "must be implemented in subclass"

    def __getitem__ (self, url):
        """Get rating for given url."""
        raise NotImplementedError, "must be implemented in subclass"

    def __iter__ (self):
        """Get list of stored urls."""
        raise NotImplementedError, "must be implemented in subclass"

    def keys (self):
        return [x for x in self]

    def __len__ (self):
        """Number of stored ratings."""
        raise NotImplementedError, "must be implemented in subclass"

    def __contains__ (self, url):
        """True if rating for given url is stored."""
        raise NotImplementedError, "must be implemented in subclass"

    def check_url (self, url):
        if not wc.url.is_safe_url(url):
            raise wc.filter.rating.RatingParseError(
                                  "Invalid rating url %s." % repr(url))

    def load (self):
        pass

    def write (self):
        pass


# mapping {class name -> storage class instance}
_stored = {}
def get_rating_store (klass):
    name = klass.__name__
    if name not in _stored:
        _stored[name] = klass()
    return _stored[name]
