"""filter a HTML stream."""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
import re, sys, wc
from wc.parser.htmllib import HtmlParser
from Rules import STARTTAG, ENDTAG, DATA, COMMENT
from wc import debug,error
from wc.debug_levels import *
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter.Filter import Filter

orders = [FILTER_RESPONSE_MODIFY]
rulenames = ['rewrite','nocomments']

_noquoteval = re.compile("^[a-zA-Z0-9_]+$")

class Rewriter(Filter):
    """This class can rewrite HTML tags. It uses a parser class."""
    mimelist = ('text/html',)


    def __init__(self):
        self.rules = []
        self.comments = 1


    def addrule(self, rule):
        debug(BRING_IT_ON, "enable %s rule '%s'"%(rule.get_name(),rule.title))
        if rule.get_name()=='rewrite':
            if rule.enclosed:
                rule.enclosed = re.compile(rule.enclosed)
            for key,val in rule.attrs.items():
                rule.attrs[key] = re.compile(rule.attrs[key])
            self.rules.append(rule)
        elif rule.get_name()=='nocomments':
            self.comments = 0


    def filter(self, data, **attrs):
        if not attrs.has_key('filter'): return data
        debug(NIGHTMARE, "Rewriter filter", "\n"+`"..."+data[-70:]`)
        p = attrs['filter']
        p.feed(data)
        return p.flushbuf()


    def finish(self, data, **attrs):
        if not attrs.has_key('filter'): return data
        debug(NIGHTMARE, "Rewriter finish", "\n"+`"..."+data[-70:]`)
        p = attrs['filter']
        p.feed(data)
        p.flush()
        p.buffer2data()
        return p.flushbuf()


    def getAttrs(self, headers, url):
        """We need a separate filter instance for stateful filtering"""
        p = HtmlFilter(self.rules, self.comments, url)
        return {'filter': p}



class HtmlFilter(HtmlParser):
    """The parser has the rules, a data buffer and a rule stack."""
    def __init__(self, rules, comments, url):
        if wc.config['showerrors']:
            self.error = self._error
            self.warning = self._warning
            self.fatalError = self._fatalError
        HtmlParser.__init__(self)
        self.rules = rules
        self.comments = comments
        self.data = ""
        self.rulestack = []
        self.buffer = []
        self.document = url or "unknown"


    def __repr__(self):
        return "<HtmlFilter with rulestack %s >" % self.rulestack


    def buffer_append_data(self, data):
        """we have to make sure that we have no two following
        DATA things in the buffer. Why? well, just to be 100% sure
        that an ENCLOSED match really matches enclosed data.
        """
        if self.buffer and data[0]==DATA and self.buffer[-1][0]==DATA:
            self.buffer[-1][1] += data[1]
        else:
            self.buffer.append(data)


    def cdataBlock(self, d):
        """handler for data"""
        self.buffer_append_data([DATA, d])


    def ignorableWhitespace(self, d):
        """handler for ignorable whitespace"""
        self.buffer_append_data([DATA, d])


    def flushbuf(self):
        """flush internal data buffer"""
        data = self.data
        if data:
            self.data = ""
        return data


    def buffer2data(self):
        """Append all tags of the buffer to the data"""
        for n in self.buffer:
            if n[0]==DATA:
                self.data += n[1]
            elif n[0]==COMMENT:
                self.data += "<!--%s-->"%n[1]
            elif n[0]==STARTTAG:
                s = "<"+n[1]
                for name,val in n[2].items():
                    s += ' %s'%name
                    if val:
                        if _noquoteval.match(val):
                            s += "=%s"%val
                        elif val.find('"')!=-1:
                            s += "='%s'"%val
                        else:
                            s += '="%s"'%val
                self.data += s+">"
            elif n[0]==ENDTAG:
                self.data += "</%s>"%n[1]
            else:
                error("unknown buffer element %s" % n[0])
        self.buffer = []


    def comment (self, data):
        """a comment. If we accept comments, filter them because JavaScript
	is often in wrapped in comments"""
        if self.comments:
            self.buffer.append([COMMENT, data])


    def characters (self, s):
        self.buffer_append_data([DATA, s])


    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        rulelist = []
        tobuffer = (STARTTAG, tag, attrs)
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                debug(NIGHTMARE, "matched rule %s on tag %s" % (`rule.title`, `tag`))
                if rule.start_sufficient:
                    tobuffer = rule.filter_tag(tag, attrs)
                    # give'em a chance to replace more than one attribute
                    if tobuffer[0]==STARTTAG and tobuffer[1]==tag:#.lower()==tag:
                        foo,tag,attrs = tobuffer
                        continue
                    else:
                        break
                else:
                    debug(NIGHTMARE, "put on buffer")
                    rulelist.append(rule)
        if rulelist:
            self.rulestack.append((len(self.buffer), rulelist))
        self.buffer_append_data(tobuffer)
        if not self.rulestack:
            self.buffer2data()


    def endElement(self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the buffer (by calling buffer2data)"""
        self.buffer.append((ENDTAG, tag))
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag):
            i, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(i, self.buffer):
                    rule.filter_complete(i, self.buffer)
                    break
        if not self.rulestack:
            self.buffer2data()


    def internalSubset (self, name, externId, systemId):
        s = "<!DOCTYPE HTML "
        if externId:
            s += 'PUBLIC "%s">'%name
        elif systemId:
            s += 'SYSTEM "%s">'%name
        else:
            s += '"%s"'%name
        self.buffer_append_data([DATA, s])


    def errorfun(self, line, col, msg, name):
        print >> sys.stderr, name, "parsing %s:%d:%d: %s" % \
            (self.document, line, col, msg.strip())


    def _error(self, line, col, msg):
        self.errorfun(line, col, msg, "error")


    def _warning(self, line, col, msg):
        self.errorfun(line, col, msg, "warning")


    def _fatalError(self, line, col, msg):
        self.errorfun(line, col, msg, "fatalError")
