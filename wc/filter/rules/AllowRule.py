# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Block URLs.
"""

from . import UrlRule
from ...XmlUtils import xmlquoteattr


class AllowRule(UrlRule.UrlRule):
    """
    Define a regular expression for urls to be allowed, even if they
    would be blocked by a block rule otherwise.
    See also the Blocker filter module.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, url="", matchurls=None, nomatchurls=None):
        """
        Initialize rule data.
        """
        super(AllowRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.url = url
        self.attrnames.append('url')

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s =  super(AllowRule, self).toxml() + \
             u'\n url="%s"' % xmlquoteattr(self.url)
        s += self.endxml()
        return s
