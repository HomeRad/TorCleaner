# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

class LimitQueue (object):
    def __init__ (self, capacity=100):
        if capacity<1:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._queue = []


    def append (self, obj):
        self._queue.append(obj)
        if len(self._queue)>self._capacity:
            del self._queue[0]


    def getall (self):
        q, self._queue = self._queue, []
        return q
