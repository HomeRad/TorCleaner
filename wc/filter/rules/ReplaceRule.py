# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Rule replacing parts of text.
"""
from . import UrlRule, Rule
from wc.XmlUtils import xmlquote, xmlquoteattr


class ReplaceRule(UrlRule.UrlRule):
    """
    This rule can Replace parts of text data according to regular expressions.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, search="", replacement=""):
        """
        Initialize rule attributes.
        """
        super(ReplaceRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        self.search = search
        self.replacement = replacement
        self.attrnames.append('search')

    def end_data(self, name):
        """
        Store replacement data.
        """
        super(ReplaceRule, self).end_data(name)
        if name == 'replacement':
            self.replacement = self._data

    def compile_data(self):
        """
        Compile url regular expressions.
        """
        super(ReplaceRule, self).compile_data()
        Rule.compileRegex(self, "search")

    def update(self, rule, dryrun=False, log=None):
        """
        Update rule attributes with given rule data.
        """
        chg = super(ReplaceRule, self).update(rule, dryrun=dryrun, log=log)
        return self.update_attrs(['replacement'], rule, dryrun, log) or chg

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = super(ReplaceRule, self).toxml()
        if self.search:
            s += u'\n search="%s"' % xmlquoteattr(self.search)
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.replacement:
            s += u'\n  <replacement>%s</replacement>' % \
              xmlquote(self.replacement)
        s += u"\n</%s>" % self.name
        return s
