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

from Rule import Rule
from wc.XmlUtils import xmlify


class AllowRule (Rule):
    def __init__ (self, sid=None, title="No title", desc="",
                  disable=0, scheme="", url=""):
        super(AllowRule, self).__init__(sid=sid, title=title,
                                        desc=desc, disable=disable)
        self.url = url
        self.attrnames.append('url')


    def fromFactory (self, factory):
        return factory.fromAllowRule(self)


    def toxml (self):
        return super(AllowRule, self).toxml() + \
           '\n url="%s"/>' % xmlify(self.url)
