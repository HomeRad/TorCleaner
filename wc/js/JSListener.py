class JSListener:
    def processData (self, data):
        raise NotImplementedError("abstract method")
    def processPopup (self):
        raise NotImplementedError("abstract method")
