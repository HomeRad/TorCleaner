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

# every filter applies to a list of filter stages which
# are described in filter/__init__.py
orders = []
# every filter specifies which rules apply to it
rulenames = []

# The base filter class
class Filter:
    def addrule(self, rule):
        pass

    def filter(self, data, **args):
        return apply(self.doit, (data,), args)

    def finish(self, data, **args):
        return apply(self.doit, (data,), args)

    def doit(self, data, **args):
        return data

    def getAttrs(self, headers, url):
        return {}

