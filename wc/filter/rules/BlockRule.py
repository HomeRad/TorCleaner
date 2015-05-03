# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Block URLs.
"""
from . import AllowRule
import wc.XmlUtils


class BlockRule(AllowRule.AllowRule):
    """
    Define a regular expression for urls to be blocked, and a
    replacement url with back references for matched subgroups.
    See also the Blocker filter module.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, url="", replacement="", matchurls=None,
                  nomatchurls=None):
        """
        Initialize rule data.
        """
        super(BlockRule, self).__init__(sid=sid, titles=titles,
                          descriptions=descriptions, disable=disable, url=url,
                          matchurls=matchurls, nomatchurls=nomatchurls)
        self.replacement = replacement

    def end_data(self, name):
        """
        Store replacement data.
        """
        super(BlockRule, self).end_data(name)
        if name == 'replacement':
            self.replacement = self._data

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s =  super(AllowRule.AllowRule, self).toxml() + \
             u'\n url="%s"' % wc.XmlUtils.xmlquoteattr(self.url)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.replacement:
            s += u"\n  <replacement>%s</replacement>" % \
              wc.XmlUtils.xmlquote(self.replacement)
        s += u"\n</%s>" % self.name
        return s
