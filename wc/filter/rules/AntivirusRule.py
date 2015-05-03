# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Filter viruses.
"""
from . import UrlRule


class AntivirusRule(UrlRule.UrlRule):
    """
    If enabled, tells the VirusFilter to scan web content for viruses.
    """

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        return super(AntivirusRule, self).toxml() + self.endxml()
