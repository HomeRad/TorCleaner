# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Hold a list of urls/domains to filter in external files, like those
found in SquidGuard.
"""
from . import Rule
import wc.XmlUtils


class ExternfileRule(Rule.Rule):
    """
    Rule with data stored in a (compressed) external file, used for
    huge url and domain block lists.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, filename=None):
        """
        Initialize rule attributes.-
        """
        super(ExternfileRule, self).__init__(sid=sid, titles=titles,
                                  descriptions=descriptions, disable=disable)
        self.filename = filename
        self.attrnames.append('filename')

    def __str__(self):
        """
        Return rule data as string.
        """
        return "%sfile %s\n" % \
            (super(ExternfileRule, self).__str__(), repr(self.filename))

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(ExternfileRule, self).toxml()
        s += u' filename="%s"' % wc.XmlUtils.xmlquoteattr(self.filename)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        s += u"\n</%s>" % self.name
        return s
