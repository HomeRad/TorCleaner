"""basic filter class"""
# Copyright (C) 2000,2001 Bastian Kleineidam
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
import re
from wc import debug
from wc.debug_levels import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = []
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = []

# The base filter class
class Filter:
    def __init__ (self):
        self.rules = []

    def addrule (self, rule):
        debug(BRING_IT_ON, "enable %s rule '%s'"%(rule.get_name(),rule.title))
        self.rules.append(rule)

    def filter (self, data, **args):
        return apply(self.doit, (data,), args)

    def finish (self, data, **args):
        return apply(self.doit, (data,), args)

    def doit (self, data, **args):
        return data

    def getAttrs (self, headers, url):
        return {'url': url, 'headers': headers}

    # XXX class method
    def compileRegex (self, obj, attr):
        if hasattr(obj, attr) and getattr(obj, attr):
            setattr(obj, attr, re.compile(getattr(obj, attr)))
