# -*- coding: iso-8859-1 -*-
"""apply rule to specific urls"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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

import re
from Rule import Rule, compileRegex
from wc.XmlUtils import xmlify, unxmlify
from wc.log import *


class UrlRule (Rule):
    """rule which applies only to urls which match a regular expression"""
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, matchurls=[], nomatchurls=[]):
        """initialize rule attributes"""
        super(UrlRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        self.matchurls = []
        self.nomatchurls = []
        self.matchurls.extend(matchurls)
        self.nomatchurls.extend(nomatchurls)


    def appliesTo (self, url):
        """return True iff this rule can be applied to given url"""
        for mo in self.matchurls_ro:
            if mo.search(url):
                return True
        if self.matchurls:
            return False
        for mo in self.nomatchurls_ro:
            if mo.search(url):
                return False
        return True


    def end_data (self, name):
        if name=='matchurl':
            self.matchurls.append(unxmlify(self._data).encode('iso8859-1'))
        elif name=='nomatchurl':
            self.nomatchurls.append(unxmlify(self._data).encode('iso8859-1'))
        else:
            super(UrlRule, self).end_data(name)


    def compile_data (self):
        """compile url regular expressions"""
        super(UrlRule, self).compile_data()
        self.compile_matchurls()
        self.compile_nomatchurls()


    def compile_matchurls (self):
        self.matchurls_ro = [re.compile(s) for s in self.matchurls]


    def compile_nomatchurls (self):
        self.nomatchurls_ro = [re.compile(s) for s in self.nomatchurls]


    def matchestoxml (self, prefix=""):
        """match url rule data as XML for storing"""
        m = ["%s<matchurl>%s</matchurl>" % \
             (prefix, xmlify(r)) for r in self.matchurls]
        n = ["%s<nomatchurl>%s</nomatchurl>" % \
             (prefix, xmlify(r)) for r in self.nomatchurls]
        return "\n".join(m+n)


    def __str__ (self):
        """return rule data as string"""
        return super(UrlRule, self).__str__() + \
            "matchurls %s\n" % str(self.matchurls) + \
            "nomatchurls %s\n" % str(self.nomatchurls)
