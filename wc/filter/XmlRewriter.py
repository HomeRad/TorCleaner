# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter a XML stream.
"""
import sys
import re
import xml.sax.handler
from xml.sax import expatreader
from . import Filter, STAGE_RESPONSE_MODIFY
from .xmlfilt import XmlFilter
from .. import log, LOG_FILTER

DefaultCharset = 'iso-8859-1'

unquoted_amp = re.compile(r"&(?!#?[a-zA-Z0-9]+;)")

class XmlRewriter(Filter.Filter):
    """
    This filter can rewrite XML tags. It uses an expat parser.
    """

    enable = True

    def __init__(self):
        """
        Init XML stages and mimes.
        """
        stages = [STAGE_RESPONSE_MODIFY]
        rulenames = ['xmlrewrite', 'htmlrewrite']
        mimes = ['text/xml', 'application/((rss|atom|rdf)\+)?xml', ]
        super(XmlRewriter, self).__init__(stages=stages, rulenames=rulenames,
                                          mimes=mimes)

    def filter(self, data, attrs):
        """
        Feed data to XML parser.
        """
        if 'xmlrewriter_parser' not in attrs:
            return data
        p = attrs['xmlrewriter_parser']
        f = attrs['xmlrewriter_filter']
        data2 = unquoted_amp.sub("&amp;", data)
        try:
            p.feed(data2)
        except xml.sax.SAXException:
            evalue = sys.exc_info()[1]
            log.error(LOG_FILTER, "XML filter error at %s: %s",
                         attrs['url'], str(evalue))
            return data
        return f.getoutput()

    def finish(self, data, attrs):
        """
        Feed data to XML parser and flush buffers.
        """
        if 'xmlrewriter_parser' not in attrs:
            return data
        p = attrs['xmlrewriter_parser']
        f = attrs['xmlrewriter_filter']
        try:
            if data:
                p.feed(data)
            p.close()
        except xml.sax.SAXException, msg:
            log.error(LOG_FILTER, "XML finish error at %s: %s",
                         attrs['url'], str(msg))
            return data
        return f.getoutput()

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        We need a separate filter instance for stateful filtering.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(XmlRewriter, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        xmlrules = []
        htmlrules = []
        for rule in self.rules:
            if not rule.applies_to_url(url):
                continue
            if rule.name == u'xmlrewrite':
                xmlrules.append(rule)
            elif rule.name == u'htmlrewrite':
                htmlrules.append(rule)
        encoding = attrs.get("charset", "UTF-8")
        handler = XmlFilter.XmlFilter(xmlrules, htmlrules, url,
            localhost, encoding)
        p = expatreader.ExpatParser(namespaceHandling=1)
        p.setContentHandler(handler)
        p.setFeature(xml.sax.handler.feature_external_ges, 0)
        # Note: expat does not read external parameter entities, so
        # setting feature_external_pes is not necessary
        attrs['xmlrewriter_parser'] = p
        attrs['xmlrewriter_filter'] = handler
