# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
URL rating storage.
"""
from __future__ import with_statement
import os
import cPickle as pickle
import urlparse

from .. import log, LOG_FILTER, LOG_RATING, fileutil, url as urlutil


def make_safe_url(url):
    """Remove unsafe parts of url for rating cache check."""
    parts = split_url(url)
    pathparts = [make_safe_part(x) for x in parts[2:]]
    return "".join(parts[0:2] + pathparts)


def make_safe_part(part):
    """Remove unsafe chars of url."""
    if part == '/':
        return part
    return filter(urlutil.is_safe_char, part)


def split_url(url):
    """
    Split an url into parts suitable for longest prefix match

    @return: parts so that "".join(parts) == url
    @rtype: list
    """
    # split into [scheme, host, path, query, fragment]
    parts = list(urlparse.urlsplit(url))
    if not (parts[0] and parts[1]):
        log.warn(LOG_FILTER, "invalid url for rating split: %r", url)
        return []
    # fix scheme
    parts[0] += ":"
    if parts[0] != 'mailto':
        parts[0] += "//"
    # remove query and fragment
    del parts[3:5]
    # further split path in components
    parts[2:] = split_path(parts[2])
    return parts


def split_path(path):
    """
    Split a path into parts suitable for longest prefix match

    @return: parts so that "".join(parts) == path
    @rtype: list
    """
    parts = [ p for p in path.split("/") if p ]
    if not parts:
        return ['/']
    ret = []
    for p in parts:
        ret.extend(['/', p])
    return ret


class UrlRatingStorage(object):

    def __init__(self, configdir):
        self.filename = os.path.join(configdir, "rating.dat")
        self.cache = {}
        if os.path.isfile(self.filename):
            self.load()

    def load(self):
        """Load pickled cache from disk."""
        with open(self.filename, 'rb') as fp:
            self.cache = pickle.load(fp)
        # remove invalid entries
        toremove = []
        for url in self.cache:
            if url != make_safe_url(url):
                log.warn(LOG_RATING, "Invalid rating url %r", url)
                toremove.append(url)
        if toremove:
            for url in toremove:
                del self.cache[url]
            self.write()

    def write(self):
        """Write pickled cache to disk."""
        def callback(fp, obj):
            pickle.dump(obj, fp, 1)
        fileutil.write_file(self.filename, self.cache, callback=callback)

    def __setitem__(self, url, rating):
        """Add rating for given url."""
        url = make_safe_url(url)
        self.cache[url] = rating

    def __getitem__(self, url):
        """Get rating for given url."""
        url = make_safe_url(url)
        # use a specialized form of longest prefix matching:
        # split the url in parts and the longest matching part wins
        parts = split_url(url)
        # the range selects from all parts (full url) down to the first two parts
        for i in xrange(len(parts), 1, -1):
            url = "".join(parts[:i])
            if url in self.cache:
                return self.cache[url]
        raise KeyError(url)

    def __contains__(self, url):
        try:
            self[url]
            return True
        except KeyError:
            return False

    def keys(self):
        return sorted(self.cache.keys())

    def __iter__(self):
        """Iterate over stored rating urls."""
        return iter(sorted(self.cache.keys()))

    def __len__(self):
        """Number of stored ratings."""
        return len(self.cache)

    def __delitem__(self, url):
        """Remove rating for given url."""
        url = make_safe_url(url)
        del self.cache[url]
