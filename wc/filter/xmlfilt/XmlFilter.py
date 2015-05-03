# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
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
Filter XML tags.
"""

from StringIO import StringIO
from ... import log, LOG_XML, containers, strformat
from . import (STARTDOCUMENT, ENDDOCUMENT, INSTRUCTION, STARTTAG, ENDTAG,
    DATA, tagbuf2data)


def dict_attrs (attrs):
    _attrs = containers.ListDict()
    for name in attrs.getQNames():
        _attrs[name] = attrs.getValueByQName(name)
    return _attrs


class XmlFilter (object):
    """
    Filtering XML parser handler. Has filter rules and a rule stack.
    """

    def __init__ (self, xmlrules, htmlrules, url, localhost, encoding):
        """
        Init rules and buffers.
        """
        # filter rules
        self.xmlrules = xmlrules
        self.htmlrules = htmlrules
        self.url = url
        # current namespaces
        self.ns_current = []
        # stacked namespaces
        self.ns_stack = []
        # already filtered XML data
        self.outbuf = StringIO()
        self.tagbuf = []
        self.rulestack = []
        self.stack = []
        if strformat.is_encoding(encoding):
            self.encoding = encoding
        else:
            self.encoding = "UTF-8"
            log.info(LOG_XML, "Invalid XML encoding %r at %r corrected to %r",
                        encoding, self.url, self.encoding)

    # ErrorHandler methods

    def error (self, msg):
        """
        Report a filter/parser error.
        """
        log.error(LOG_XML, msg)

    def fatalError (self, msg):
        """
        Report a fatal filter/parser error.
        """
        log.critical(LOG_XML, msg)

    def warning (self, msg):
        """
        Report a filter/parser warning.
        """
        log.warn(LOG_XML, msg)

    # ContentHandler methods

    def setDocumentLocator (self, locator):
        # A Locator is not used here.
        pass

    def startDocument (self):
        """
        Nothing to do here.
        """
        attrs = {
            u"version": u"1.0",
            u"encoding": self.encoding,
            # XXX no info about 'standalone'
        }
        item = [STARTDOCUMENT, u"xml", attrs]
        self.tagbuf.append(item)

    def endDocument (self):
        """
        Nothing to do here.
        """
        item = [ENDDOCUMENT]
        self.tagbuf.append(item)

    def startPrefixMapping (self, prefix, uri):
        ns = (prefix, uri)
        self.ns_stack.append(ns)
        self.ns_current.append(ns)

    def endPrefixMapping (self, prefix):
        if not self.ns_stack or self.ns_stack[-1][0] != prefix:
            self.error("Removing unknown prefix mapping (%r)" % prefix)
        del self.ns_stack[-1]

    def find_namespace (self, uri):
        for prefix, nsuri in reversed(self.ns_stack):
            if nsuri == uri:
                return (prefix, uri)
        return None

    def startElement (self, name, attrs):
        attrs = dict_attrs(attrs)
        for prefix, uri in self.ns_current:
            if prefix:
                attrs["xmlns:%s" % prefix] = uri
            else:
                attrs["xmlns"] = uri
        self.ns_current = []
        self.stack.append((STARTTAG, name, attrs))
        item = [STARTTAG, name, attrs]
        self.tagbuf.append(item)
        rulelist = [rule for rule in self.xmlrules \
                    if rule.match_tag(self.stack)]
        if rulelist:
            pos = len(self.tagbuf)
            self.rulestack.append((pos, rulelist))

    def endElement (self, name):
        item = [ENDTAG, name]
        if not self.filter_end_element(name):
            self.tagbuf.append(item)
        if not self.rulestack:
            self.tagbuf2data()
        del self.stack[-1]

    def filter_end_element (self, tag):
        """
        Filters an end tag, return True if tag was filtered, else False.
        """
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(self.stack):
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                rule.filter_tag(pos, self.tagbuf, tag, self.url,
                                self.htmlrules)
            return True
        return False

    def startElementNS (self, name, qname, attrs):
        tag = name[1]
        namespace = self.find_namespace(name[0])
        if namespace and namespace[0]:
            tag = u"%s:%s" % (namespace[0], name[1])
        self.startElement(tag, attrs)

    def endElementNS (self, name, qname):
        tag = name[1]
        namespace = self.find_namespace(name[0])
        if namespace and namespace[0]:
            tag = u"%s:%s" % (namespace[0], name[1])
        self.endElement(tag)

    def characters (self, content):
        if self.tagbuf and self.tagbuf[-1][0] == DATA:
            self.tagbuf[-1][1] += content
        else:
            self.tagbuf.append([DATA, content])

    def ignorableWhitespace (self, chars):
        pass

    def processingInstruction (self, target, data):
        item = [INSTRUCTION, target, data]
        self.tagbuf.append(item)

    def skippedEntity (self, name):
        """
        An unknown entity was found, for example '&foo;'.
        """
        self.tagbuf.append([DATA, u"&%s;" % name])

    # DTDHandler methods

    def notationDecl (self, name, publicId, systemId):
        """
        DTD content is ignored.
        """
        log.info(LOG_XML, "%s: DTD notation ignored: %r %r %r",
            self, name, publicId, systemId)

    def unparsedEntityDecl (self, name, publicId, systemId, ndata):
        """
        DTD content is ignored.
        """
        log.info(LOG_XML, "%s: DTD entity ignored: %r %r %r %r",
              self, name, publicId, systemId, ndata)

    # other methods

    def tagbuf2data (self):
        """
        Append serialized tag items of the tag buffer to the output buffer
        and clear the tag buffer.
        """
        tagbuf2data(self.tagbuf, self.outbuf)
        self.tagbuf = []

    def getoutput (self):
        """
        Returns all data in output buffer and clears the output buffer.
        """
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data.encode(self.encoding, "ignore")

    def __repr__ (self):
        """
        Representation with state.
        """
        return "<XmlFilter %s>" % self.url
