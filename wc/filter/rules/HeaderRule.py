# -*- coding: iso-8859-1 -*-
"""Filter HTTP headers"""
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

from UrlRule import UrlRule
from wc.XmlUtils import xmlify, unxmlify

class HeaderRule (UrlRule):
    """rule for filtering HTTP headers"""

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, name="noname", value=""):
        """init rule name and value"""
        super(HeaderRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        self.name = name
        self.value = value
        self.attrnames.append('name')


    def end_data (self, name):
        super(HeaderRule, self).end_data(name)
        if name=='replacement':
            self.value = unxmlify(self._data).encode('iso8859-1')
            self._reset_parsed_data()


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromHeaderRule(self)


    def update (self, rule, dryrun=False, log=None):
        """update header data"""
        chg = super(HeaderRule, self).update(rule, dryrun=dryrun, log=log)
        return self.update_attrs(['value'], rule, dryrun, log) or chg


    def toxml (self):
        """Rule data as XML for storing"""
        s = '%s\n name="%s">' % \
            (super(HeaderRule, self).toxml(), xmlify(self.name))
        s += "\n"+self.title_desc_toxml()
        s += "\n"+self.matchestoxml()
        if self.value:
            s += ' <replacement>%s</replacement>' % xmlify(self.value)
        s += "</%s>" % self.get_name()
        return s
