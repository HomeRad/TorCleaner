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
    def __init__ (self, sid=None, title="No title", desc="",
                  disable=0, url="", replacement=""):
        """initialize rule data"""
        super(BlockRule, self).__init__(sid=sid, title=title,
                                        desc=desc, disable=disable, url=url)
        self.replacement = replacement


    def fill_data (self, data, name):
        """add replacement text"""
        super(BlockRule, self).fill_data(data, name)
        if name=='block':
            self.replacement += data


    def compile_data (self):
        """unquote replacement text"""
        super(BlockRule, self).compile_data()
        self.replacement = unxmlify(self.replacement).encode('iso8859-1')


    def fromFactory (self, factory):
        """rule factory"""
        return factory.fromBlockRule(self)


    def toxml (self):
        """Rule data as XML for storing"""
        # chop off the last two chars '/>'
        s =  super(AllowRule, self).toxml() + \
             '\n url="%s" replacement="%s">\n' % \
             (xmlify(self.url), xmlify(self.replacement))
        s += self.matchestoxml()
        s += "</%s>" % self.get_name()
        return s
