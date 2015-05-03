# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
JavaScript filter rule.
"""
from . import UrlRule


class JavascriptRule(UrlRule.UrlRule):
    """
    If enabled, this rule tells the HtmlRewriter to filter JavaScript.
    """

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(JavascriptRule, self).toxml()
        s += self.endxml()
        return s
