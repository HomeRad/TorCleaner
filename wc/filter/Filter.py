# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.log import *

class Filter (object):
    """the base filter class"""
    def __init__ (self, apply_to_mimelist):
        self.rules = []
        self.apply_to_mimelist = apply_to_mimelist


    def addrule (self, rule):
        debug(FILTER, "enable %s rule %s", rule.get_name(), `rule.title`)
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
        if not self.apply_to_mimelist:
            return True
        for ro in self.apply_to_mimelist:
            if ro.match(mime):
                return True
        return False
