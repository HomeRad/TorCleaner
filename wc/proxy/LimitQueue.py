# -*- coding: iso-8859-1 -*-
"""a size limited queue"""


class LimitQueue (object):
    """size limited queues do not exceed a given capacity by removing
       oldest entries"""

    def __init__ (self, capacity=100):
        """capacity must be > 0"""
        if capacity<1:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._queue = []

    def append (self, obj):
        """enqueue given obj"""
        if len(self._queue) == self._capacity:
            del self._queue[0]
        self._queue.append(obj)

    def getall (self):
        """flush the queue, returning all currently stored entries"""
        q, self._queue = self._queue, []
        return q

