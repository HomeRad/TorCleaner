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
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc import _,debug,error
from wc.debug_levels import *
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, compileRegex
from wc.filter.Filter import Filter

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['rewrite','nocomments']
mimelist = map(compileMime, ['text/html'])

# regular expression which matches tag attributes that dont
# need to be quoted
# modern browsers can cope with a lot of non-quoted content
_noquoteval = re.compile("^[-+~a-zA-Z0-9_/.#%:?,$]+$")

class Rewriter (Filter):
    """This filter can rewrite HTML tags. It uses a parser class."""

    def __init__ (self, mimelist):
        Filter.__init__(self, mimelist)
        self.comments = 1

    def addrule (self, rule):
        Filter.addrule(self, rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")
        if rule.get_name()=='rewrite':
            compileRegex(rule, "enclosed")
            for key,val in rule.attrs.items():
                rule.attrs[key] = re.compile(rule.attrs[key])
        elif rule.get_name()=='nocomments':
            self.comments = 0

    def filter (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        #debug(NIGHTMARE, "Rewriter filter", "\n...%s"%`data[-70:]`)
        p = attrs['filter']
        p.feed(data)
        return p.flushbuf()

    def finish (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        #debug(NIGHTMARE, "Rewriter finish", "\n...%s"%`data[-70:]`)
        p = attrs['filter']
        if data: p.feed(data)
        p.flush()
        p.buffer2data()
        return p.flushbuf()

    def getAttrs (self, headers, url):
        """We need a separate filter instance for stateful filtering"""
        # first: weed out the rules that dont apply to this url
        rules = filter(lambda r, u=url: r.appliesTo(u), self.rules)
        # second: weed out the comments rules, but remember length
        before = len(rules)
        rules = filter(lambda r: r.get_name()=='rewrite', rules)
        # generate the HTML filter
        return {'filter': HtmlFilter(rules, (len(rules)==before), url)}


class HtmlFilter (HtmlParser):
    """The parser has the rules, a data buffer and a rule stack."""
    def __init__ (self, rules, comments, url):
        if wc.config['showerrors']:
            self.error = self._error
            self.warning = self._warning
            self.fatalError = self._fatalError
        HtmlParser.__init__(self)
        self.rules = rules
        self.comments = comments
        self.data = []
        self.rulestack = []
        self.buffer = []
        self.document = url or "unknown"

    def __repr__ (self):
        return "<HtmlFilter with rulestack %s >" % self.rulestack

    def buffer_append_data (self, data):
        """we have to make sure that we have no two following
        DATA things in the buffer. Why? To be 100% sure that
        an ENCLOSED match really matches enclosed data.
        """
        if self.buffer and data[0]==DATA and self.buffer[-1][0]==DATA:
            self.buffer[-1][1] += data[1]
        else:
            self.buffer.append(data)

    def cdata (self, d):
        """handler for data"""
        self.buffer_append_data([DATA, d])

    def flushbuf (self):
        """flush internal data buffer"""
        data = "".join(self.data)
        if data:
            self.data = []
        return data

    def buffer2data (self):
        """Append all tags of the buffer to the data"""
        for n in self.buffer:
            if n[0]==DATA:
                self.data.append(n[1])
            elif n[0]==COMMENT:
                self.data.append("<!--%s-->"%n[1])
            elif n[0]==STARTTAG:
                s = "<"+n[1]
                for name,val in n[2].items():
                    s += ' %s'%name
                    if val:
                        s += "=%s"%val
                self.data.append(s+">")
            elif n[0]==ENDTAG:
                self.data.append("</%s>"%n[1])
            else:
                error(_("unknown buffer element %s") % n[0])
        self.buffer = []

    def comment (self, data):
        """a comment: accept only non-empty comments"""
        if self.comments and data:
            self.buffer.append([COMMENT, data])

    def characters (self, s):
        self.buffer_append_data([DATA, s])

    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        rulelist = []
        # default data
        tobuffer = (STARTTAG, tag, attrs)
        # look for filter rules which apply
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                #debug(NIGHTMARE, "matched rule %s on tag %s" % (`rule.title`, `tag`))
                if rule.start_sufficient:
                    tobuffer = rule.filter_tag(tag, attrs)
                    # give'em a chance to replace more than one attribute
                    if tobuffer[0]==STARTTAG and tobuffer[1]==tag:
                        foo,tag,attrs = tobuffer
                        continue
                    else:
                        break
                else:
                    #debug(NIGHTMARE, "put on buffer")
                    rulelist.append(rule)
        if rulelist:
            self.rulestack.append((len(self.buffer), rulelist))
        self.buffer_append_data(tobuffer)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack:
            self.buffer2data()

    def endElement (self, tag):
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

    def doctype (self, data):
        self.buffer_append_data([DATA, "<!DOCTYPE%s>"%data])

    def pi (self, data):
        self.buffer_append_data([DATA, "<?%s?>"%data])

    def errorfun (self, msg, name):
        print >> sys.stderr, name, _("parsing %s: %s") % \
            (self.document, msg)

    def _error (self, msg):
        self.errorfun(msg, "error")


    def _warning (self, msg):
        self.errorfun(msg, "warning")

    def _fatalError (self, msg):
        self.errorfun(msg, "fatalError")
