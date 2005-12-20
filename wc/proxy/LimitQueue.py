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
"""
A size limited queue.
"""


class LimitQueue (object):
    """
    Size limited queue. Does not exceed a given capacity by removing
    oldest entries.
    """

    def __init__ (self, capacity=100):
        """
        Capacity must be > 0.
        """
        if capacity < 1:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._queue = []

    def append (self, obj):
        """
        Enqueue given obj.
        """
        if len(self._queue) == self._capacity:
            del self._queue[0]
        self._queue.append(obj)

    def getall (self):
        """
        Flush the queue, returning all currently stored entries.
        """
        q, self._queue = self._queue, []
        return q
