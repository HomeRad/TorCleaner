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
Directory storage.
"""

import re
import os
import wc.filter.rating.storage


is_time = re.compile(r"^\d+$").search


class DirectoryStorage (wc.filter.rating.storage.Storage):
    """
    Store ratings in as plain file data in dictionaries.
    """

    def __init__ (self):
        super(DirectoryStorage, self).__init__()
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



def rating_cache_parse (fp):
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
