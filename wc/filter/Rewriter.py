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
import re, sys, urlparse, time, wc
from wc import urlutils
from wc.parser.htmllib import HtmlParser
from wc.parser import resolve_html_entities
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc.debug import *
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, compileRegex
from wc.filter.Filter import Filter
# JS imports
from wc.js.JSListener import JSListener
from wc.js import jslib

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['rewrite','nocomments','javascript']
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
        debug(NIGHTMARE, "Filter: Rewrite", "\n...%s"%`data[-70:]`)
        p = attrs['filter']
        p.feed(data)
        return p.flushbuf()

    def finish (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        debug(NIGHTMARE, "Filter: Rewrite finish", "\n...%s"%`data[-70:]`)
        p = attrs['filter']
        if data: p.feed(data)
        p.flush()
        p.buffer2data()
        return p.flushbuf()

    def getAttrs (self, headers, url):
        """We need a separate filter instance for stateful filtering"""
        rewrites = []
        opts = {'comments': 1, 'javascript': 0}
        for rule in self.rules:
            if not rule.appliesTo(url): continue
            if rule.get_name()=='rewrite':
                rewrites.append(rule)
            elif rule.get_name()=='nocomments':
                opts['comments'] = 0
            elif rule.get_name()=='javascript':
                opts['javascript'] = 1
        # generate the HTML filter
        return {'filter': HtmlFilter(rewrites, url, **opts)}


class HtmlFilter (HtmlParser,JSListener):
    """The parser has the rules, a data buffer and a rule stack."""
    def __init__ (self, rules, url, **opts):
        if wc.config['showerrors']:
            self.error = self._error
            self.warning = self._warning
            self.fatalError = self._fatalError
        HtmlParser.__init__(self)
        self.rules = rules
        self.comments = opts['comments']
        self.javascript = opts['javascript']
        self.data = []
        self.rulestack = []
        self.buffer = []
        self.url = url or "unknown"
        if self.javascript:
            self.jsEnv = jslib.new_jsenv()
            self.output_counter = 0
            self.popup_counter = 0

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
            elif n[0]==STARTTAG:
                s = "<"+n[1]
                for name,val in n[2].items():
                    s += ' %s'%name
                    if val:
                        s += "=%s"%val
                self.data.append(s+">")
            elif n[0]==ENDTAG:
                self.data.append("</%s>"%n[1])
            elif n[0]==COMMENT:
                self.data.append("<!--%s-->"%n[1])
            else:
                error("unknown buffer element %s" % n[0])
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
        filtered = 0
        # default data
        tobuffer = (STARTTAG, tag, attrs)
        # look for filter rules which apply
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                debug(NIGHTMARE, "Filter: matched rule %s on tag %s" % (`rule.title`, `tag`))
                if rule.start_sufficient:
                    tobuffer = rule.filter_tag(tag, attrs)
                    filtered = "True"
                    # give'em a chance to replace more than one attribute
                    if tobuffer[0]==STARTTAG and tobuffer[1]==tag:
                        foo,tag,attrs = tobuffer
                        continue
                    else:
                        break
                else:
                    debug(NIGHTMARE, "Filter: put on buffer")
                    rulelist.append(rule)
        if rulelist:
            # remember buffer position for end tag matching
            pos = len(self.buffer)
            self.rulestack.append((pos, rulelist))
        # if its not yet filtered, try filter javascript
        if filtered:
            self.buffer_append_data(tobuffer)
        elif self.javascript:
            self.jsStartElement(tag, attrs)
        else:
            self.buffer.append(tobuffer)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and \
           (not self.javascript or tag!='script'):
            self.buffer2data()


    def jsStartElement (self, tag, attrs):
        """Check popups for onmouseout and onmouseover.
           Inline extern javascript sources (only in the
           same domain)"""
        changed = 0
        for name in ('onmouseover', 'onmouseout'):
            if attrs.has_key(name) and self.jsPopup(attrs, name):
                del attrs[name]
                changed = 1
        if tag=='form':
            name = attrs.get('name', attrs.get('id'))
            self.jsForm(name, attrs.get('action', ''), attrs.get('target', ''))
        # fetching JS script src is too much delay
        #elif tag=='script':
        #    lang = attrs.get('language', '').lower()
        #    scrtype = attrs.get('type', '').lower()
        #    if scrtype=='text/javascript' or \
        #       lang.startswith('javascript') or \
        #       not (lang or scrtype):
        #        if self.jsScriptSrc(attrs.get('src', ''), lang):
        #            return
        self.buffer.append((STARTTAG, tag, attrs))


    def jsPopup (self, attrs, name):
        """check if attrs[name] javascript opens a popup window"""
        val = resolve_html_entities(attrs[name])
        if not val: return
        self.jsEnv.attachListener(self)
        try:
            self.jsEnv.executeScriptAsFunction(val, 0.0)
        except jslib.error, msg:
            pass
        self.jsEnv.detachListener(self)
        res = self.popup_counter
        self.popup_counter = 0
        return res


    def jsForm (self, name, action, target):
        if not name: return
        debug(HURT_ME_PLENTY, "Filter: jsForm", `name`, `action`, `target`)
        self.jsEnv.addForm(name, action, target)


    def jsScriptSrc (self, url, language):
        if not url: return
        url = urlparse.urljoin(self.url, url)
        debug(HURT_ME_PLENTY, "Filter: jsScriptSrc", url, language)
        try:
            debug(BRING_IT_ON, "fetching", url, time.ctime(time.time()))
            script = urlutils.open_url(url).read()
            debug(BRING_IT_ON, "...fetched", time.ctime(time.time()))
        except:
            print >>sys.stderr, "exception fetching script url", `url`
            import traceback
            traceback.print_exc()
            return
        if not script: return
        ver = 0.0
        if language:
            mo = re.search(r'(?i)javascript(?P<num>\d\.\d)', language)
            if mo:
                ver = float(mo.group('num'))
        if self.jsScript(script, ver):
            print >> sys.stderr, "JS popup src", url, "url", url
            return "True"


    def jsScript (self, script, ver):
        """execute given script with javascript version ver
           return True if the script generates any output, else False"""
        debug(HURT_ME_PLENTY, "Filter: jsScript", script, ver)
        self.output_counter = 0
        self.jsEnv.attachListener(self)
        self.jsfilter = HtmlFilter(self.rules, self.url,
                 comments=self.comments, javascript=self.javascript)
        self.jsEnv.executeScript(script, ver)
        self.jsEnv.detachListener(self)
        if self.output_counter:
            self.jsfilter.flush()
            self.data.append(self.jsfilter.flushbuf())
            self.buffer += self.jsfilter.buffer
            self.rulestack += self.jsfilter.rulestack
        self.jsfilter = None
        return self.output_counter


    def processData (self, data):
        # parse recursively
        self.output_counter += 1
        self.jsfilter.feed(data)


    def processPopup (self):
        self.popup_counter += 1


    def endElement (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the buffer (by calling buffer2data)"""
        filtered = 0
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag):
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.buffer):
                    rule.filter_complete(pos, self.buffer)
                    filtered = 1
                    break
        if not filtered and self.javascript and tag=='script' and \
            self.jsEndElement(tag):
            del self.buffer[-1]
            del self.buffer[-1]
        else:
            self.buffer.append((ENDTAG, tag))
        if not self.rulestack:
            self.buffer2data()


    def jsEndElement (self, tag):
        """parse generated html for scripts
           return True if the script generates any output, else False"""
        if len(self.buffer)<2:
            return
        if self.buffer[-1][0]!=DATA:
            print >>sys.stderr, "missing data for </script>", self.buffer[-1:]
            return
        script = self.buffer[-1][1].strip()
        if not (self.buffer[-2][0]==STARTTAG and \
                self.buffer[-2][1]=='script'):
            # there was a <script src="..."> already
            return
        # remove html comments
        if script.startswith("<!--"):
            i = script.index('\n')
            if i==-1:
                script = script[4:]
            else:
                script = script[(i+1):]
        if script.endswith("-->"):
            script = script[:-3]
        if not script: return
        return self.jsScript(script, 0.0)


    def doctype (self, data):
        self.buffer_append_data([DATA, "<!DOCTYPE%s>"%data])


    def pi (self, data):
        self.buffer_append_data([DATA, "<?%s?>"%data])

    def errorfun (self, msg, name):
        print >> sys.stderr, name, "parsing %s: %s" % (self.url, msg)

    def _error (self, msg):
        self.errorfun(msg, "error")

    def _warning (self, msg):
        self.errorfun(msg, "warning")

    def _fatalError (self, msg):
        self.errorfun(msg, "fatalError")
