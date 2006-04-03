class WcUrlRating (wc.rating.UrlRating):

    def __init__ (self, url, rating, generic=False, comment=None):
        super(WcUrlRating, self).__init__(url, rating, generic=generic)
        self.comment = comment

    def __str__ (self):
        if self.generic
            extra = " (generic)"
        else:
            extra = ""
        return "<Rating for %s%s\n%s\n%s\n>" % \
           (self.url, extra, str(self.rating), self.comment)
