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
Pickle storage.
"""

import os
import cPickle as pickle

import wc
import wc.log
import wc.url
import wc.filter.rating
import wc.filter.rating.storage


class PickleStorage (wc.filter.rating.storage.Storage):
    """
    Store ratings in a pickled dictionary.
    """

    def __init__ (self):
        """
        Initialize and load.
        """
        super(PickleStorage, self).__init__()
        config = wc.configuration.config
        self.filename = os.path.join(config.configdir, "rating.dat")
        self.cache = {}
        self.load()

    def __setitem__ (self, url, rating):
        """
        Add rating for given url.
        """
        self.check_url(url)
        self.cache[url] = rating

    def __getitem__ (self, url):
        """
        Get rating for given url.
        """
        self.check_url(url)
        # use a specialized form of longest prefix matching:
        # split the url in parts and the longest matching part wins
        parts = wc.filter.rating.split_url(url)
        # the range selects from all parts (full url) down to the first two parts
        for i in range(len(parts), 1, -1):
            url = "".join(parts[:i])
            if url in self.cache:
                return self.cache[url]
        raise KeyError, url

    def __contains__ (self, url):
        """
        True if rating for given url is stored.
        """
        self.check_url(url)
        # use a specialized form of longest prefix matching:
        # split the url in parts and the longest matching part wins
        parts = wc.filter.rating.split_url(url)
        # the range selects from all parts (full url) down to the first two parts
        for i in range(len(parts), 1, -1):
            url = "".join(parts[:i])
            if url in self.cache:
                return True
        return False

    def __iter__ (self):
        """
        Iterate over stored rating urls.
        """
        return iter(self.cache)

    def __len__ (self):
        """
        Number of stored ratings.
        """
        return len(self.cache)

    def __delitem__ (self, url):
        """
        Remove rating for given url.
        """
        self.check_url(url)
        del self.cache[url]

    def write (self):
        """
        Write pickled cache to disk.
        """
        fp = file(self.filename, 'wb')
        pickle.dump(self.cache, fp, 1)
        fp.close()

    def load (self):
        """
        Load pickled cache from disk.
        """
        if os.path.isfile(self.filename):
            fp = file(self.filename, 'rb')
            self.cache = pickle.load(fp)
            fp.close()
            # remove invalid entries
            toremove = []
            for url in self.cache:
                if not wc.url.is_safe_url(url):
                    wc.log.error(wc.LOG_RATING, "Invalid rating url %r", url)
                    toremove.append(url)
            if toremove:
                for url in toremove:
                    del self[url]
                self.write()
