"""replace expressions in a data stream
you can use this for
- highlighting
- removing certain strings
"""
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
from string import lower
from Rules import STARTTAG, ENDTAG, DATA, COMMENT
from wc import debug,error
from wc.debug_levels import *
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter.Filter import Filter

orders = [FILTER_RESPONSE_MODIFY]
rulenames = ['replace']


class Replacer(Filter):
    """This class can replace regular expressions a data stream."""
    mimelist = ('text/html',
        'text/javascript')

    def __init__(self):
        self.rules = []


    def addrule(self, rule):
        debug(BRING_IT_ON, "enable %s rule '%s'"%(rule.get_name(),rule.title))
        if rule.get_name()=='replace':
            if rule.search:
                rule.search = re.compile(rule.search)
            self.rules.append(rule.search, rule.replacement)

    def filter(self, data, **args):
        # add to buffer
        apply(self.doit, (data,), args)

    def finish(self, data, **args):
        # add to buffer
        apply(self.doit, (data,), args)
        # flush buffer

    def doit(self, data, **args):
        for ro,repl in self.rules:
            data = self.replace_one(self, ro, repl, data)
        return data


    def replace_one(self, ro, repl, data):
        # XXX
        return data
