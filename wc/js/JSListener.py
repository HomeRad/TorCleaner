class JSListener:
    """Define handler functions for javascript events"""

    def jsProcessData (self, data):
        """handler for document.write content"""
        raise NotImplementedError("abstract method jsProcessData")

    def jsProcessPopup (self):
        """handler for popup windows"""
        raise NotImplementedError("abstract method jsProcessPopup")

    def jsProcessError (self, err):
        """handler for syntax errors"""
        raise NotImplementedError("abstract method jsProcessError")
