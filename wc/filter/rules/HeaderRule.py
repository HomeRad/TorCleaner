# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter HTTP headers.
"""
from . import UrlRule
import wc.XmlUtils


class HeaderRule(UrlRule.UrlRule):
    """
    Rule for filtering HTTP headers.
    """

    def __init__(self, sid=None, titles=None, descriptions=None,
                  disable=0, header="noname", value="", filterstage="request",
                  action="remove", matchurls=None, nomatchurls=None):
        """
        Init rule name and value.
        """
        super(HeaderRule, self).__init__(sid=sid, titles=titles,
                                 descriptions=descriptions, disable=disable,
                                 matchurls=matchurls, nomatchurls=nomatchurls)
        self.header = header
        self.value = value
        self.filterstage = filterstage
        self.action = action
        self.attrnames.extend(('header', 'filterstage', 'action'))

    def end_data(self, name):
        """
        Store replacement data.
        """
        super(HeaderRule, self).end_data(name)
        if name == 'replacement':
            self.value = self._data
            if self.value and self.action == "remove":
                self.action = "replace"

    def fill_attrs(self, attrs, name):
        """
        Set attribute values.
        """
        super(HeaderRule, self).fill_attrs(attrs, name)
        if name == "header":
            self.header = attrs["name"]

    def update(self, rule, dryrun=False, log=None):
        """
        Update header data.
        """
        chg = super(HeaderRule, self).update(rule, dryrun=dryrun, log=log)
        return self.update_attrs(['value'], rule, dryrun, log) or chg

    def __str__(self):
        """
        Return rule data as string.
        """
        return super(HeaderRule, self).__str__() + \
            ("name %r\nvalue %r\nstage %s" %
             (self.header, self.value, self.filterstage))

    def toxml(self):
        """
        Rule data as XML for storing.
        """
        s = u'%s\n name="%s"' % (super(HeaderRule, self).toxml(),
                                wc.XmlUtils.xmlquoteattr(self.header))
        s += u'\n filterstage="%s"' % self.filterstage
        s += u'\n action="%s"' % self.action
        s += u">\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.value:
            s += u'\n  <replacement>%s</replacement>' % \
               wc.XmlUtils.xmlquote(self.value)
        s += u"\n</%s>" % self.name
        return s
