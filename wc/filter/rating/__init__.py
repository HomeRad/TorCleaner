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
Rating related data types and routines.
"""

import urlparse

import wc
import wc.configuration
import wc.containers
import wc.log
import wc.url


class RatingParseError (Exception):
    """
    Raised on parsing errors.
    """
    pass


def make_safe_url (url):
    """
    Remove unsafe parts of url for rating cache check.
    """
    parts = wc.filter.rating.split_url(url)
    pathparts = [make_safe_part(x) for x in parts[2:]]
    pathparts[0:2] = parts[0:2]
    return "".join(pathparts)


def make_safe_part (part):
    """
    Remove unsafe chars of url.
    """
    if part == '/':
        return part
    return filter(wc.url.is_safe_char, part)


def split_url (url):
    """
    Split an url into parts suitable for longest prefix match

    @return: parts so that "".join(parts) == url
    @rtype: list
    """
    # split into [scheme, host, path, query, fragment]
    parts = list(urlparse.urlsplit(url))
    if not (parts[0] and parts[1]):
        wc.log.warn(wc.LOG_FILTER, "invalid url for rating split: %r", url)
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


def split_path (path):
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


services = wc.containers.SetList()
def register_service (service):
    """
    Register the given service in the services list.
    """
    services.append(service)
    for category in service.categories:
        register_category(category)


categories = wc.containers.SetList()
def register_category (category):
    """
    Register the given category in the categories list.
    """
    categories.append(category)


def get_service (service_name):
    """
    Get service instance for given name or None if not found.
    """
    for service in services:
        if service.name == service_name:
            return service
    # not found
    return None


def get_category (category_name):
    """
    Get category instance for given name or None if not found.
    """
    for category in categories:
        if category.name == category_name:
            return category
    # not found
    return None


def XXXrating_cache_merge (newrating_cache, dryrun=False, log=None):
    """
    Add new ratings, but do not change existing ones.
    """
    chg = False
    for url, rating in newrating_cache.iteritems():
        if url not in rating_cache:
            chg = True
            print >> log, _("adding new rating for %r") % url
            if not dryrun:
                rating_cache[url] = rating
    if not dryrun and chg:
        rating_cache_write()
    return chg
