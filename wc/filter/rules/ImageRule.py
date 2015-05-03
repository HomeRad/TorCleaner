# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter images by size.
"""
from . import UrlRule
from wc.XmlUtils import xmlquoteattr


class ImageRule(UrlRule.UrlRule):
    """
    If enabled, tells the Image filter to block certain images.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, width=0, height=0, formats=None, url="",
                  matchurls=None, nomatchurls=None):
        """
        Initalize rule data.
        """
        super(ImageRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.width = width
        self.height = height
        self.intattrs.extend(('width', 'height'))
        self.listattrs.append('formats')
        if formats is None:
            self.formats = []
        else:
            self.formats = formats
        self.url = url
        self.attrnames.extend(('formats', 'url', 'width', 'height'))

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(ImageRule, self).toxml()
        if self.width:
            s += u'\n width="%d"' % self.width
        if self.height:
            s += u'\n height="%d"' % self.height
        if self.formats:
            s += u'\n formats="%s"' % \
                 xmlquoteattr(",".join(self.formats))
        if self.url:
            s += u'\n url="%s"' % xmlquoteattr(self.url)
        s += self.endxml()
        return s
