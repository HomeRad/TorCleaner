class JSListener:
    def jsProcessData (self, data):
        raise NotImplementedError("abstract method")
    def jsProcessPopup (self):
        raise NotImplementedError("abstract method")
