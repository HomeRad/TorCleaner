# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Apply rule to specific URLs.
"""
import re
from . import MimeRule
from wc.XmlUtils import xmlquote


class UrlRule(MimeRule.MimeRule):
    """
    Rule which applies only to URLs which match a regular expression.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, matchurls=None, nomatchurls=None, mimes=None):
        """
        Initialize rule attributes.
        """
        super(UrlRule, self).__init__(sid=sid, titles=titles,
                     descriptions=descriptions, disable=disable, mimes=mimes)
        if matchurls is None:
            self.matchurls = []
        else:
            self.matchurls = matchurls
        self.matchurls_ro = None
        if nomatchurls is None:
            self.nomatchurls = []
        else:
            self.nomatchurls = nomatchurls
        self.nomatchurls_ro = None

    def applies_to_url(self, url):
        """
        Return True iff this rule can be applied to given URL.
        """
        for mo in self.matchurls_ro:
            if mo.search(url):
                return True
        if self.matchurls:
            return False
        for mo in self.nomatchurls_ro:
            if mo.search(url):
                return False
        return True

    def end_data(self, name):
        """
        Store matchurl and nomatchurl data.
        """
        super(UrlRule, self).end_data(name)
        if name == 'matchurl':
            self.matchurls.append(self._data)
        elif name == 'nomatchurl':
            self.nomatchurls.append(self._data)

    def compile_data(self):
        """
        Compile regular expressions.
        """
        super(UrlRule, self).compile_data()
        self.compile_matchurls()
        self.compile_nomatchurls()

    def compile_matchurls(self):
        """
        Compile matchurls regular expressions.
        """
        self.matchurls_ro = [re.compile(s) for s in self.matchurls]

    def compile_nomatchurls(self):
        """
        Compile nomatchurls regular expressions.
        """
        self.nomatchurls_ro = [re.compile(s) for s in self.nomatchurls]

    def matchestoxml(self, prefix=u""):
        """
        Match URL rule data as XML for storing.
        """
        m = [u"%s<matchurl>%s</matchurl>" % \
             (prefix, xmlquote(r)) for r in self.matchurls]
        n = [u"%s<nomatchurl>%s</nomatchurl>" % \
             (prefix, xmlquote(r)) for r in self.nomatchurls]
        return u"\n".join(m+n)

    def endxml(self):
        """
        Return ending part of XML serialization with title and matches.
        """
        s = u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.mimes:
            s += u"\n"+self.mimestoxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.name
        return s

    def __str__(self):
        """
        Return rule data as string.
        """
        return super(UrlRule, self).__str__() + \
            "matchurls %s\n" % str(self.matchurls) + \
            "nomatchurls %s\n" % str(self.nomatchurls)
