# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Filter a HTML stream.
"""

import xml.sax
import xml.sax.expatreader

import wc.filter
import wc.filter.Filter
import wc.filter.xmlfilt.XmlFilter

DefaultCharset = 'iso-8859-1'

class XmlRewriter (wc.filter.Filter.Filter):
    """
    This filter can rewrite XML tags. It uses an expat parser.
    """

    def __init__ (self):
        """
        Init stages and mimes.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ['xmlrewrite', 'htmlrewrite']
        mimes = ['text/xml', 'application/xml', 'application/atom+xml']
        super(XmlRewriter, self).__init__(stages=stages, rulenames=rulenames,
                                          mimes=mimes)

    def filter (self, data, attrs):
        """
        Feed data to XML parser.
        """
        if not attrs.has_key('xmlrewriter_parser'):
            return data
        p = attrs['xmlrewriter_parser']
        f = attrs['xmlrewriter_filter']
        if data:
            try:
                p.feed(data)
            except xml.sax.SAXException, msg:
                wc.log.error(wc.LOG_FILTER, "XML filter error at %s: %s",
                             attrs['url'], str(msg))
                return data
        return f.getoutput()

    def finish (self, data, attrs):
        """
        Feed data to XML parser and flush buffers.
        """
        if not attrs.has_key('xmlrewriter_parser'):
            return data
        p = attrs['xmlrewriter_parser']
        f = attrs['xmlrewriter_filter']
        try:
            if data:
                p.feed(data)
            p.close()
        except xml.sax.SAXException, msg:
            wc.log.error(wc.LOG_FILTER, "XML finish error at %s: %s",
                         attrs['url'], str(msg))
            return data
        return f.getoutput()

    def get_attrs (self, url, localhost, stages, headers):
        """
        We need a separate filter instance for stateful filtering.
        """
        if not self.applies_to_stages(stages):
            return {}
        d = super(XmlRewriter, self).get_attrs(
                                             url, localhost, stages, headers)
        xmlrules = []
        htmlrules = []
        for rule in self.rules:
            if not rule.applies_to(url):
                continue
            if rule.get_name() == u'xmlrewrite':
                xmlrules.append(rule)
            elif rule.get_name() == u'htmlrewrite':
                htmlrules.append(rule)
        handler = wc.filter.xmlfilt.XmlFilter.XmlFilter(xmlrules, htmlrules,
                                                        url, localhost)
        p = xml.sax.expatreader.ExpatParser(namespaceHandling=1)
        p.setContentHandler(handler)
        d['xmlrewriter_parser'] = p
        d['xmlrewriter_filter'] = handler
        return d
