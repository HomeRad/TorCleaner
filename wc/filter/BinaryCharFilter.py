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
from wc.filter import FILTER_RESPONSE_MODIFY, Filter, compileMime

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = []
# which mime types this filter applies to
mimelist = map(compileMime, ['text/html'])


class BinaryCharFilter (Filter):

    def doit (self, data, **attrs):
        return data.translate('\x00\x84\x91\x92\x93\x94', ' "`\'""')
