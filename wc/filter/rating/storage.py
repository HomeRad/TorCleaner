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

import os
import cPickle as pickle
import re

import wc
import wc.decorators
import wc.log
import wc.url
import wc.filter.rating


class Storage (object):
    """
    Basic storage class for ratings.
    """

    @wc.decorators.notimplemented
    def __setitem__ (self, url, rating):
        """
        Add rating for given url.
        """
        pass

    @wc.decorators.notimplemented
    def __delitem__ (self, url):
        """
        Remove rating for given url.
        """
        pass

    @wc.decorators.notimplemented
    def __getitem__ (self, url):
        """
        Get rating for given url.
        """
        pass

    @wc.decorators.notimplemented
    def __iter__ (self):
        """
        Iterate over stored urls.
        """
        pass

    def keys (self):
        """
        Return list of urls for whom ratings are stored.
        """
        return [x for x in self]

    @wc.decorators.notimplemented
    def __len__ (self):
        """
        Number of stored ratings.
        """
        pass

    @wc.decorators.notimplemented
    def __contains__ (self, url):
        """
        True if rating for given url is stored.
        """
        pass

    def check_url (self, url):
        """
        If url is not safe raise a RatingParseError.
        """
        if not wc.url.is_safe_url(url):
            raise wc.filter.rating.RatingParseError, \
                                  "Invalid rating url %s." % repr(url)

    @wc.decorators.notimplemented
    def load (self):
        """
        Load stored data into this instance.
        """
        pass

    @wc.decorators.notimplemented
    def write (self):
        """
        Write data of this instance.
        """
        pass

    def merge (self, newstorage, dryrun=False, log=None):
        """
        Add new ratings, but do not change existing ones.
        """
        chg = False
        for url, rating in newstorage.iteritems():
            if url not in self:
                chg = True
                print >> log, _("adding new rating for %r") % url
                if not dryrun:
                    self[url] = rating
        if not dryrun and chg:
            self.write()
        return chg


class PickleStorage (Storage):
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
        wc.log.debug(wc.LOG_RATING, "Write ratings to %r", self.filename)
        def callback (fp, obj):
            pickle.dump(obj, fp, 1)
        wc.fileutil.write_save(self.filename, self.cache, callback=callback)

    def load (self):
        """
        Load pickled cache from disk.
        """
        wc.log.debug(wc.LOG_RATING, "Loading ratings from %r", self.filename)
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
	else:
	    wc.log.debug(wc.LOG_RATING, "Not a plain file: %r", self.filename)


is_time = re.compile(r"^\d+$").search


class FileStorage (Storage):
    """
    Store ratings in plain text files in dictionaries.
    """

    def __init__ (self):
        super(FileStorage, self).__init__()
        pass # XXX


def rating_import (url, ratingdata, debug=0):
    """
    Parse given rating data, throws ParseError on error.
    """
    categories = {}
    for line in ratingdata.splitlines():
        if debug:
            wc.log.debug(wc.LOG_RATING, "Read line %r", line)
        line = line.strip()
        if not line:
            # ignore empty lines
            continue
        if line.startswith("#"):
            # ignore comments
            continue
        try:
            category, value = line.split(None, 1)
        except ValueError:
            raise RatingParseError, _("malformed rating line %r") % line
        if category == "modified" and not is_time(value):
            raise RatingParseError, _("malformed modified time %r") % value
        if category == "generic" and value not in ["true", "false"] and \
           not url.startswith(value):
            raise RatingParseError, _(
                            "generic url %r doesn't match %r") % (value, url)
        categories[category] = value
    return categories


def rating_export (rating):
    """
    Return string representation of given rating data.
    """
    return "\n".join([ "%s %s"%item for item in rating.items() ])
    # XXX


def rating_exportall ():
    """
    Export all ratings in a text file called `rating.txt', located
    in the same directory as the file `rating.dat'.
    """
    config = wc.configuration.config
    fp = file(os.path.join(config.configdir, "rating.txt"), 'w')
    for url, rating in rating_cache.iteritems():
        if not wc.url.is_safe_url(url):
            wc.log.error(wc.LOG_RATING, "invalid url %r", url)
            continue
        fp.write("url %s\n"%url)
        fp.write(rating_export(rating))
        fp.write("\n\n")
    fp.close()


def rating_parse (fp):
    """
    Parse previously exported rating data from given file.
    """
    url = None
    ratingdata = []
    newrating_cache = {}
    for line in fp:
        line = line.rstrip('\r\n')
        if not line:
            if url:
                data = "\n".join(ratingdata)
                newrating_cache[url] = rating_import(url, data)
            url = None
            ratingdata = []
            continue
        if line.startswith('url'):
            url = line.split()[1]
        elif url:
            ratingdata.append(line)
    return newrating_cache

