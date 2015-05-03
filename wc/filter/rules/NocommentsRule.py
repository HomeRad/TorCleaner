# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
HTML comments filter rule.
"""
from . import UrlRule


class NocommentsRule(UrlRule.UrlRule):
    """
    If enabled, this rule tells the HtmlRewriter to remove HTML comments.
    """

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(NocommentsRule, self).toxml()
        s += self.endxml()
        return s
