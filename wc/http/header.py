# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

import cStringIO as StringIO
import rfc822


class WcMessage (rfc822.Message, object):
    """
    Represents a single RFC 2822-compliant message, adding functions
    handling multiple headers with the same name.
    """

    def __init__ (self, fp=None, seekable=True):
        """
        Initialize message reading from given optional file descriptor.
        """
        if fp is None:
            fp = StringIO.StringIO()
        super(WcMessage, self).__init__(fp, seekable=seekable)

    def remove_multiple_headers (self, name):
        """
        Remove all occurrences of given header name except the first.
        """
        values = self.getheaders(name)
        if len(values) > 1:
            self[name] = values[0]
            return True
        return False

    def addheader (self, name, value):
        """
        Add given header name and value to the end of the header list.
        Multiple headers with the same name are supported.
        """
        text = name + ": " + value
        lines = text.split('\n')
        for line in lines:
            self.headers.append(line + "\n")
        self.dict[name] = value

    def __str__ (self):
        """
        HTTP conform string representation.
        """
        return "\n".join([ repr(s) for s in self.headers ])

    def copy (self):
        """
        Copy these headers into a new WcHeaders object.
        """
        return WcMessage(fp=StringIO.StringIO("".join(self.headers)))
