# Copyright (C) 2000-2002  Bastian Kleineidam
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

# all parts of a URL

from Rule import Rule
from wc import xmlify, unxmlify
Netlocparts = [
        'scheme',
        'host',
        'port',
        'path',
        'parameters',
        'query',
        'fragment',
    ]

class AllowRule (Rule):
    def __init__ (self, title="No title", desc="", disable=0, scheme="",
                  host="", port="", path="", parameters="", query="",
		  fragment="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path
        self.parameters = parameters
        self.query = query
        self.fragment = fragment
        self.attrnames.extend(('scheme','host','port','path','parameters',
                                'query','fragment'))

    def fromFactory (self, factory):
        return factory.fromAllowRule(self)

    def toxml (self):
        return "%s%s/>"%(Rule.toxml(self),self.netlocxml())

    def netlocxml (self):
        s = ""
        for attr in Netlocparts:
            a = getattr(self, attr)
            if a is not None:
                s += '\n %s="%s"' % (attr, xmlify(a))
        return s

