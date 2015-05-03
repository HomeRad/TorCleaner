# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2009 Bastian Kleineidam
import time
from .. import UrlRating


class WcUrlRating(UrlRating):

    def __init__(self, url, rating, generic=False, comment=None):
        super(WcUrlRating, self).__init__(url, rating, generic=generic)
        self.comment = comment
        self.modified = time.time()

    def __str__(self):
        lines = []
        if self.generic:
            extra = " (generic)"
        else:
            extra = ""
        lines.append("<Rating for %s%s" % (self.url, extra))
        for item in self.rating.items():
            lines.append(" %s=%s" % item)
        lines.append(" comment=%s" % self.comment)
        return "\n".join(lines)
