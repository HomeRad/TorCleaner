# Copyright (C) 2000-2002  Bastian Kleineidam
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
from wc.debug import *

class Filter:
    """the base filter class"""
    def __init__ (self, mimelist):
        self.rules = []
        self.mimelist = mimelist

    def addrule (self, rule):
        debug(HURT_ME_PLENTY, "Filter: enable %s rule '%s'"%(rule.get_name(),rule.title))
        self.rules.append(rule)

    def filter (self, data, **args):
        return apply(self.doit, (data,), args)

    def finish (self, data, **args):
        return apply(self.doit, (data,), args)

    def doit (self, data, **args):
        return data

    def getAttrs (self, headers, url):
        return {'url': url, 'headers': headers}

    def applies_to_mime (self, mime):
        if not self.mimelist:
            return 1
        for ro in self.mimelist:
            if ro.match(mime):
                return 1
