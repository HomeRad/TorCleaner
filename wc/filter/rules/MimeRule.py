# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2007 Bastian Kleineidam
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
"""
Apply rule to specific MIME types.
"""

import re
import Rule
import wc.XmlUtils


class MimeRule (Rule.Rule):
    """
    Rule which applies only to given MIME types.
    """

    def __init__ (self, sid=None, titles=None, descriptions=None,
                  disable=0, mimes=None):
        """
        Initialize rule attributes.
        """
        super(MimeRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        if mimes is None:
            self.mimes = []
        else:
            self.mimes = mimes
        self.mimes_ro = None

    def applies_to_mime (self, mime):
        """
        Return True iff this rule can be applied to given MIME type.
        """
        for mo in self.mimes_ro:
            if mo.search(mime):
                return True
        if self.mimes:
            return False
        return True

    def end_data (self, name):
        """
        Store MIME data.
        """
        super(MimeRule, self).end_data(name)
        if name == 'mime':
            self.mimes.append(self._data)

    def compile_data (self):
        """
        Compile regular expressions.
        """
        super(MimeRule, self).compile_data()
        self.compile_mimes()

    def compile_mimes (self):
        """
        Compile MIME regular expressions.
        """
        self.mimes_ro = [re.compile(s) for s in self.mimes]

    def mimestoxml (self, prefix=u""):
        """
        Match url rule data as XML for storing.
        """
        m = [u"%s<mime>%s</mime>" % \
             (prefix, wc.XmlUtils.xmlquote(r)) for r in self.mimes]
        return u"\n".join(m)

    def endxml (self):
        """
        Return ending part of XML serialization with title and matches.
        """
        s = u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.mimes:
            s += u"\n"+self.mimestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.name
        return s

    def __str__ (self):
        """
        Return rule data as string.
        """
        return super(MimeRule, self).__str__() + \
            "mimes %s\n" % str(self.mimes)
