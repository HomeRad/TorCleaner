# Copyright (C) 2003  Bastian Kleineidam
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

from UrlRule import UrlRule
from wc import i18n
from wc.XmlUtils import xmlify, unxmlify

class PicsRule (UrlRule):
    """holds configured PICS rating data"""
    def __init__ (self, title="No title", desc="", disable=0, oid=0):
        UrlRule.__init__(self, title=title, desc=desc,disable=disable,oid=oid)
        self.ratings = {}
        self.url = ""


    def fill_attrs (self, attrs, name):
        if name=='service':
            self._service = unxmlify(attrs.get('name')).encode('iso8859-1')
            self.ratings[self._service] = {}
        elif name=='category':
            assert self._service
            self._category = unxmlify(attrs.get('name')).encode('iso8859-1')
        elif name=='url':
            pass
        elif name=='pics':
            UrlRule.fill_attrs(self, attrs, name)
        else:
            raise ValueError(i18n._("Invalid pics rule tag name `%s',"+\
                                    " check your configuration")%name)


    def fill_data (self, data, name):
        data = unxmlify(data).encode('iso8859-1')
        if name=='category':
            assert self._service
            assert self._category
            assert self.ratings.has_key(self._service)
            self.ratings[self._service][self._category] = int(data)
        elif name=='url':
            self.url = data
        else:
            # ignore other content
            pass


    def toxml (self):
	s = UrlRule.toxml(self)+">\n"
        if self.url:
            s += "<url>%s</url>\n" % xmlify(self.url)
        for service, data in self.ratings.items():
            s += "<service name=\"%s\">\n"%xmlify(service)
            for category, value in data.items():
                s += "<category name=\"%s\">%d</category>\n"% \
                      (xmlify(category), value)
            s += "</service>\n"
        return s+"</pics>"


    def fromFactory (self, factory):
        return factory.fromPicsRule(self)
