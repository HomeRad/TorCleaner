class LimitList:
    def __init__(self, capacity=100):
        if capacity<1:
            raise ValueError("capacity must be > 0")
        self.capacity = capacity
        self.stack = [None]*capacity
        self.clear()


    def clear(self):
        self.index = 0
        self.full = 0


    def add(self, header):
        self.stack[self.index] = header
        if self.index==self.capacity-1:
            self.index = 0
            self.full = 1
        else:
            self.index += 1


    def first(self):
        if not self.full:
            return 0
        return self.index


    def next(self, i):
        if self.full and i==self.capacity-1 and self.capacity>1:
            return 0
        return i+1


    def __getitem__(self, key):
        return self.stack[key]


    def hasnext(self, i):
        if self.full:
            return (0 <= i < self.index) or (self.index <= i < self.capacity)
        return 0 <= i < self.index


def _test():
    l = LimitList(1)
    _print(l)
    l.add("1")
    _print(l)
    l.add("2")
    _print(l)
    l.clear()
    _print(l)

    l = LimitList(100)
    for i in range(0, 90):
        l.add(i)
    _print(l)


def _print(l):
    i = l.first()
    while l.hasnext(i):
        print "l[%d]=%s"%(i, l[i])
        i = l.next(i)


if __name__=='__main__':
    _test()

