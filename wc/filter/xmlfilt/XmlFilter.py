# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

import wc.url
import wc.log
import wc.filter


def dict_attrs (attrs):
    _attrs = {}
    for name in attrs.getQNames():
        _attrs[name] = attrs.getValueByQName(name)
    return _attrs


class XmlFilter (object):
    """
    Filtering XML parser handler. Has filter rules and a rule stack.
    """

    def __init__ (self, xmlrules, htmlrules, url, localhost):
        """
        Init rules and buffers.
        """
        # filter rules
        self.xmlrules = xmlrules
        self.htmlrules = htmlrules
        self.url = url
        # XML namespaces {name -> uri} and {uri -> name}
        self.prefixuri = {}
        self.uriprefix = {}
        # already filtered XML data
        self.outbuf = StringIO()
        self.tagbuf = []
        self.rulestack = []
        self.stack = []
        self.encoding = "UTF-8"

    # ErrorHandler methods

    def error (self, msg):
        """
        Report a filter/parser error.
        """
        wc.log.error(wc.LOG_FILTER, msg)

    def fatalError (self, msg):
        """
        Report a fatal filter/parser error.
        """
        wc.log.critical(wc.LOG_FILTER, msg)

    def warning (self, msg):
        """
        Report a filter/parser warning.
        """
        wc.log.warn(wc.LOG_FILTER, msg)

    # ContentHandler methods

    def setDocumentLocator (self, locator):
        print "XXX setDocumentLocator", locator

    def startDocument (self):
        """
        Nothing to do here.
        """
        attrs = {
            u"version": u"1.0",
            u"encoding": self.encoding,
        }
        item = [wc.filter.xmlfilt.STARTDOCUMENT, u"xml", attrs]
        self.tagbuf.append(item)

    def endDocument (self):
        """
        Nothing to do here.
        """
        item = [wc.filter.xmlfilt.ENDDOCUMENT]
        self.tagbuf.append(item)

    def startPrefixMapping (self, prefix, uri):
        self.prefixuri[prefix] = uri
        self.uriprefix[uri] = prefix

    def endPrefixMapping (self, prefix):
        if prefix in self.prefixuri:
            uri = self.prefixuri[prefix]
            del self.uriprefix[uri]
            del self.prefixuri[prefix]
        else:
            self.error("Removing unknown prefix mapping %r" % prefix)

    def startElement (self, name, attrs):
        attrs = dict_attrs(attrs)
        if not self.stack:
            for prefix, uri in self.prefixuri.items():
                if prefix:
                    attrs[u"xmlns:%s" % prefix] = uri
                else:
                    attrs[u"xmlns"] = uri
        self.stack.append((wc.filter.xmlfilt.STARTTAG, name, attrs))
        item = [wc.filter.xmlfilt.STARTTAG, name, attrs]
        self.tagbuf.append(item)
        rulelist = [rule for rule in self.xmlrules \
                    if rule.match_tag(self.stack)]
        if rulelist:
            pos = len(self.tagbuf)
            self.rulestack.append((pos, rulelist))

    def endElement (self, name):
        item = [wc.filter.xmlfilt.ENDTAG, name]
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
        if name[0]:
            ns = self.uriprefix[name[0]]
            if ns:
                name = u"%s:%s" % (ns, name[1])
            else:
                name = name[1]
        else:
            name = name[1]
        self.startElement(name, attrs)

    def endElementNS (self, name, qname):
        if name[0]:
            ns = self.uriprefix[name[0]]
            if ns:
                name = u"%s:%s" % (ns, name[1])
            else:
                name = name[1]
        else:
            name = name[1]
        self.endElement(name)

    def characters (self, content):
        if self.tagbuf and self.tagbuf[-1][0] == wc.filter.xmlfilt.DATA:
            self.tagbuf[-1][1] += content
        else:
            self.tagbuf.append([wc.filter.xmlfilt.DATA, content])

    def ignorableWhitespace (self, chars):
        pass

    def processingInstruction (self, target, data):
        print "XXX processingInstruction", target, data

    def skippedEntity (self, name):
        print "XXX skippedEntity", name

    # DTDHandler methods

    def notationDecl (self, name, publicId, systemId):
        print "XXX notationDecl", name, publicId, systemId

    def unparsedEntityDecl (self, name, publicId, systemId, ndata):
        print "XXX unparsedEntityDecl", name, publicId, systemId, ndata

    # other methods

    def tagbuf2data (self):
        """
        Append serialized tag items of the tag buffer to the output buffer
        and clear the tag buffer.
        """
        wc.filter.xmlfilt.tagbuf2data(self.tagbuf, self.outbuf)
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
