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
import re,string
from wc.parser.sgmllib import SGMLParser
from Rules import STARTTAG, ENDTAG, DATA, COMMENT
from wc import debug,error
from wc.debug_levels import *
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter.Filter import Filter

orders = [FILTER_RESPONSE_MODIFY]
rulenames = ['rewrite','nocomments']


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
        p = attrs['filter']
        debug(NIGHTMARE, p, `data`)
        p.feed(data)
        return p.flush()


    def finish(self, data, **attrs):
        p = attrs['filter']
        p.feed(data)
        return p.close()


    def getAttrs(self, headers):
        """We need a separate filter instance for stateful filtering"""
        p = HtmlFilter(self.rules, self.comments)
        return {'filter': p}



class HtmlFilter(SGMLParser):
    """The parser has the rules, a data buffer and a rule stack."""
    def __init__(self, rules, comments):
        SGMLParser.__init__(self)
        self.rules = rules
        self.comments = comments
        self.data = ""
        self.rulestack = []
        self.buffer = []


    def __repr__(self):
        return "<HtmlFilter with rulestack %s >" % self.rulestack

    def buffer_append_data(self, data):
        """we have to make sure that we have no two following
        DATA things in the buffer. Why? well, just to be 100% sure
        that an ENCLOSED match really matches enclosed data.
        """
        if self.buffer and data[0]==DATA and self.buffer[-1][0]==DATA:
            self.buffer[-1][1] = self.buffer[-1][1] + data[1]
        else:
            self.buffer.append(data)


    def handle_data(self, d):
        """handler for data"""
        self.buffer_append_data([DATA, d])


    def flush(self):
        data = self.data
        if data:
            self.data = ""
        return data


    def buffer2data(self):
        """Append all tags of the buffer to the data"""
        for n in self.buffer:
            if n[0]==DATA:
                self.data = self.data + n[1]
            elif n[0]==COMMENT:
                self.data = self.data+"<!--"+n[1]+"-->"
            elif n[0]==STARTTAG:
                s = "<"+n[1]
                for name,val in n[2]:
                    s = s+' '+name+'="'+val+'"'
                self.data = self.data +s+">"
            elif n[0]==ENDTAG:
                self.data = self.data+"</"+n[1]+">"
            else:
                error("unknown buffer element %s" % n[0])
        self.buffer = []


    def handle_comment(self, data):
        """a comment. either delete it or print it, nothing more
	   because we dont filter inside comments"""
        if self.comments:
            self.buffer.append((COMMENT,data))


    def handle_entityref(self, name):
        """dont translate, we leave that for the browser"""
        if name:
            name = "&"+name+";"
        else:
            # a single &, parsed by the FastSGMLParser
            # leads to an empty name
            name = "&"
        self.buffer_append_data([DATA, name])


    def handle_charref(self, name):
        """dont translate, we leave that for the browser"""
        self.buffer_append_data([DATA, "&#"+name+";"])


    def unknown_starttag(self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        rulelist = []
        tobuffer = (STARTTAG, tag, attrs)
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                debug(NIGHTMARE, "matched rule %s on tag %s" % \
		      (`rule.title`, `tag`))
                if rule.start_sufficient:
                    tobuffer = rule.filter_tag(tag, attrs)
                    # give'em a chance to replace more than one attribute
                    if tobuffer[0]==STARTTAG and \
		        string.lower(tobuffer[1])==tag:
                        _,tag,attrs = tobuffer
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


    def unknown_endtag(self, tag):
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


    def close(self):
        SGMLParser.close(self)
        self.buffer2data()
        return self.flush()
