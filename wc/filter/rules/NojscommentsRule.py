# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
HTML comments filter rule.
"""
from . import UrlRule


class NojscommentsRule(UrlRule.UrlRule):
    """
    If enabled, this rule tells the HtmlRewriter to remove JavaScript
    comments.
    """

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(NojscommentsRule, self).toxml()
        s += self.endxml()
        return s
