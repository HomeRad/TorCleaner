"""filter invalid binary chars from HTML"""
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
import string
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter.Filter import Filter

orders = [FILTER_RESPONSE_MODIFY]
rulenames = []

class BinaryCharFilter(Filter):
    mimelist = ('text/html',)

    TRANS = string.maketrans('\x00\x84\x91\x92\x93\x94', ' "`\'""')

    def filter(self, data, **attrs):
        return string.translate(data, self.TRANS)

    def finish(self, data, **attrs):
        return string.translate(data, self.TRANS)
