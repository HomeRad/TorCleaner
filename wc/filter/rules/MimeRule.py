# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Apply rule to specific MIME types.
"""
import re
from . import Rule
from wc.XmlUtils import xmlquote


class MimeRule(Rule.Rule):
    """
    Rule which applies only to given MIME types.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, mimes=None):
        """
        Initialize rule attributes.
        """
        super(MimeRule, self).__init__(sid=sid, titles=titles,
                                   descriptions=descriptions, disable=disable)
        if mimes is None:
            self.mimes = []
        else:
            self.mimes = mimes
        self.mimes_ro = None

    def applies_to_mime(self, mime):
        """
        Return True iff this rule can be applied to given MIME type.
        """
        for mo in self.mimes_ro:
            if mo.search(mime):
                return True
        if self.mimes:
            return False
        return True

    def end_data(self, name):
        """
        Store MIME data.
        """
        super(MimeRule, self).end_data(name)
        if name == 'mime':
            self.mimes.append(self._data)

    def compile_data(self):
        """
        Compile regular expressions.
        """
        super(MimeRule, self).compile_data()
        self.compile_mimes()

    def compile_mimes(self):
        """
        Compile MIME regular expressions.
        """
        self.mimes_ro = [re.compile(s) for s in self.mimes]

    def mimestoxml(self, prefix=u""):
        """
        Match url rule data as XML for storing.
        """
        return u"\n".join(u"%s<mime>%s</mime>" % (prefix, xmlquote(r))
                          for r in self.mimes)

    def endxml(self):
        """
        Return ending part of XML serialization with title and matches.
        """
        s = u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.mimes:
            s += u"\n"+self.mimestoxml(prefix=u"  ")
        s += u"\n</%s>" % self.name
        return s

    def __str__(self):
        """
        Return rule data as string.
        """
        return super(MimeRule, self).__str__() + \
            "mimes %s\n" % str(self.mimes)
