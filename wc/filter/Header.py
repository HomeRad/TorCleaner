"""webcleaner module: add or delete HTTP headers"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
from wc.filter import FILTER_REQUEST_HEADER,FILTER_RESPONSE_HEADER
from wc.filter.Filter import Filter
from wc import debug,config
from wc.debug_levels import *

orders = [FILTER_REQUEST_HEADER,
          FILTER_RESPONSE_HEADER]
rulenames = ['header']

class Header(Filter):
    def __init__(self):
        self.delete = []
        self.add = {}

    def addrule(self, rule):
        if not rule.value:
            self.delete.append(rule.name.lower())
        else:
            self.add[rule.name] = rule.value

    def doit(self, data, **args):
        for h in data.keys()[:]:
            for name in self.delete:
                if re.match(name, h):
                    data.headers.remove(h)
        for key,val in self.add.items():
            data[key] = val
        debug(HURT_ME_PLENTY, "Headers\n", data)
        return data
