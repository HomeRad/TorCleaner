# -*- coding: iso-8859-1 -*-
"""block urls"""
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

from AllowRule import AllowRule
from wc.XmlUtils import xmlify, unxmlify

class BlockRule (AllowRule):
    """Define a regular expression for urls to be blocked, and a
       replacement url with back references for matched subgroups.
       See also the Blocker filter module.
    """
    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, url="", replacement=""):
        """initialize rule data"""
        super(BlockRule, self).__init__(sid=sid, titles=titles,
                          descriptions=descriptions, disable=disable, url=url)
        self.replacement = replacement


    def end_data (self, name):
        if name=='replacement':
            self.replacement = unxmlify(self._data).encode('iso8859-1')
        else:
            super(BlockRule, self).end_data(name)


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromBlockRule(self)


    def toxml (self):
        """Rule data as XML for storing"""
        s =  super(AllowRule, self).toxml() + \
             '\n url="%s">' % xmlify(self.url)
        s += "\n"+self.title_desc_toxml(prefix="  ")
        if self.matchurls or self.nomatchurls:
            s += "\n"+self.matchestoxml(prefix="  ")
        if self.replacement:
            s += "\n  <replacement>%s</replacement>"%xmlify(self.replacement)
        s += "\n</%s>" % self.get_name()
        return s
