class LimitQueue:
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
        return map(str, q)

