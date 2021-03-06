# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Image reducer config rule.
"""
from . import UrlRule


class ImagereduceRule(UrlRule.UrlRule):
    """
    Configures the image reducer filter (if enabled).
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, quality=20, minimal_size_bytes=5120,
                  matchurls=None, nomatchurls=None):
        """
        Initalize rule data.
        """
        super(ImagereduceRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.quality = quality
        self.minimal_size_bytes = minimal_size_bytes
        self.intattrs.extend(('quality', 'minimal_size_bytes'))
        self.attrnames.extend(('quality', 'minimal_size_bytes'))

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(ImagereduceRule, self).toxml()
        s += u'\n quality="%d"' % self.quality
        s += u'\n minimal_size_bytes="%d"' % self.minimal_size_bytes
        s += self.endxml()
        return s
