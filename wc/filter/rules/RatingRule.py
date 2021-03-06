# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Filter according to rating rules.
"""
from wc.XmlUtils import xmlquote, xmlquoteattr
from wc.rating import Rating
from wc.rating.service import ratingservice
from . import UrlRule


MISSING = _("Unknown page")


class RatingRule(UrlRule.UrlRule):
    """
    Holds a rating to match against when checking for allowance of
    the rating system.
    Also stored is the url to display should a rating deny a page.
    The use_extern flag determines if the filters should parse and use
    external rating data from HTTP headers or HTML <meta> tags.
    """

    def __init__(self, sid=None, titles=None, descriptions=None, disable=0,
                  matchurls=None, nomatchurls=None, use_extern=0):
        """Initialize rating data."""
        super(RatingRule, self).__init__(sid=sid, titles=titles,
                                descriptions=descriptions, disable=disable,
                                matchurls=matchurls, nomatchurls=nomatchurls)
        self.rating = Rating()
        self.url = ""
        self.use_extern = use_extern
        self.attrnames.append('use_extern')
        self.intattrs.append('use_extern')

    def fill_attrs(self, attrs, name):
        """Init rating and url attrs."""
        super(RatingRule, self).fill_attrs(attrs, name)
        if name == 'limit':
            self._name = attrs.get('name')

    def end_data(self, name):
        """Store category or url data."""
        super(RatingRule, self).end_data(name)
        if name == 'limit':
            self.rating[self._name] = self._data
        elif name == 'url':
            self.url = self._data

    def compile_data(self):
        """Compile parsed rule values."""
        super(RatingRule, self).compile_data()
        self.compile_values()

    def compile_values(self):
        """Fill missing rating values."""
        ratingservice.rating_compile(self.rating)
        # helper dict for web gui
        self.values = {}
        for ratingformat in ratingservice.ratingformats:
            name = ratingformat.name
            self.values[name] = {}
            if ratingformat.iterable:
                for value in ratingformat.values:
                    value = str(value)
                    self.values[name][value] = value == self.rating[name]

    def toxml(self):
        """Rule data as XML for storing."""
        s = u'%s\n use_extern="%d">' % (super(RatingRule, self).toxml(),
                                        self.use_extern)
        s += u"\n"+self.title_desc_toxml(prefix=u"  ")
        if self.matchurls or self.nomatchurls:
            s += u"\n"+self.matchestoxml(prefix=u"  ")
        if self.url:
            s += u"\n  <url>%s</url>" % xmlquote(self.url)
        for name, value in self.rating.iteritems():
            value = xmlquote(str(value))
            name = xmlquoteattr(name)
            s += u"\n  <limit name=\"%s\">%s</limit>" % (name, value)
        s += u"\n</%s>" % self.name
        return s
