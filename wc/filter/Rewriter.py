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
import re, sys, urlparse, time, rfc822, wc
from cStringIO import StringIO
from wc import urlutils
from wc.parser.htmllib import HtmlParser
from wc.parser import resolve_html_entities
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc.debug import *
from wc.filter import FILTER_RESPONSE_MODIFY
from wc.filter import FilterException, compileMime, compileRegex
from wc.filter.Filter import Filter
# JS imports
from wc.js.JSListener import JSListener
from wc.js import jslib
from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
from wc.proxy.HttpProxyClient import HttpProxyClient

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
        p = attrs['filter']
        p.feed(data)
        return p.flushbuf()

    def finish (self, data, **attrs):
        if not attrs.has_key('filter'): return data
        p = attrs['filter']
        # feed even if data is empty
        p.feed(data)
        p.flush()
        p.buf2data()
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
    """The parser has the rules, a data buffer and a rule stack.
       States:
       parse => default parsing state, no background fetching
       wait  => Fetching additionally data in the background.
                Feeding new data in wait state raises a FilterException.
                When finished, the buffers look like
                data    [---------|--------][-------][----------]
                                  ^-script src tag
                waitbuf           [--------]
                inbuf                       [-------------- ...

       After a wait state, replays the waitbuf and re-feed the inbuf
       data.
    """
    def __init__ (self, rules, url, **opts):
        if wc.config['showerrors']:
            self.error = self._error
            self.warning = self._warning
            self.fatalError = self._fatalError
        HtmlParser.__init__(self)
        self.rules = rules
        self.comments = opts['comments']
        self.javascript = opts['javascript']
        self.outbuf = StringIO()
        self.inbuf = StringIO()
        self.waitbuf = []
        self.state = 'parse'
        self.script = ''
        self.waited = 0
        self.rulestack = []
        self.buf = []
        self.url = url or "unknown"
        if self.javascript:
            self.jsEnv = jslib.new_jsenv()
            self.output_counter = 0
            self.popup_counter = 0


    def __repr__ (self):
        return "<HtmlFilter with rulestack %s>" % self.rulestack


    def feed (self, data):
        if self.state=='parse':
            if self.waited:
                self.waited = 0
                waitbuf, self.waitbuf = self.waitbuf, []
                self.replay(waitbuf)
                if self.state!='parse': return
                data = self.inbuf.getvalue()
                self.inbuf.close()
                self.inbuf = StringIO()
            if data:
                debug(NIGHTMARE, "HtmlFilter: feed", `data`)
                HtmlParser.feed(self, data)
                debug(NIGHTMARE, "HtmlFilter: feed finished")
        else:
            self.inbuf.write(data)


    def flush (self):
        if self.state=='wait':
            raise FilterException("HtmlFilter: still waiting for data")
        HtmlParser.flush(self)


    def replay (self, waitbuf):
        """call the handler functions again with buffer data"""
        for item in waitbuf:
            if item[0]==DATA:
                self.characters(item[1])
            elif item[0]==STARTTAG:
                self.startElement(item[1], item[2])
            elif item[0]==ENDTAG:
                self.endElement(item[1])
            elif item[0]==COMMENT:
                self.comment(item[1])


    def buf_append_data (self, data):
        """we have to make sure that we have no two following
        DATA things in the buffer. Why? To be 100% sure that
        an ENCLOSED match really matches enclosed data.
        """
        if data[0]==DATA and self.buf and self.buf[-1][0]==DATA:
            self.buf[-1][1] += data[1]
        else:
            self.buf.append(data)


    def flushbuf (self):
        """flush internal data buffer"""
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data


    def buf2data (self):
        """Append all tags of the buffer to the data"""
        for item in self.buf:
            if item[0]==DATA:
                self.outbuf.write(item[1])
            elif item[0]==STARTTAG:
                s = "<"+item[1]
                for name,val in item[2].items():
                    s += ' %s'%name
                    if val:
                        s += "=%s"%val
                self.outbuf.write(s+">")
            elif item[0]==ENDTAG:
                self.outbuf.write("</%s>"%item[1])
            elif item[0]==COMMENT:
                self.outbuf.write("<!--%s-->"%item[1])
            else:
                error("unknown buffer element %s" % item[0])
        self.buf = []


    def cdata (self, d):
        """handler for data"""
        item = [DATA, d]
        if self.state=='wait':
            return self.waitbuf.append(item)
        self.buf_append_data(item)


    def comment (self, data):
        """a comment; accept only non-empty comments"""
        item = [COMMENT, data]
        if self.state=='wait':
            return self.waitbuf.append(item)
        if self.comments and data:
            self.buf.append(item)


    def characters (self, s):
        """handler for characters"""
        item = [DATA, s]
        if self.state=='wait':
            return self.waitbuf.append(item)
        self.buf_append_data(item)


    def doctype (self, data):
        item = [DATA, "<!DOCTYPE%s>"%data]
        if self.state=='wait':
            return self.waitbuf.append(item)
        self.buf_append_data(item)


    def pi (self, data):
        item = [DATA, "<?%s?>"%data]
        if self.state=='wait':
            return self.waitbuf.append(item)
        self.buf_append_data(item)


    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        # default data
        item = [STARTTAG, tag, attrs]
        if self.state=='wait':
            return self.waitbuf.append(item)
        rulelist = []
        filtered = 0
        # look for filter rules which apply
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                debug(NIGHTMARE, "HtmlFilter: matched rule %s on tag %s" % (`rule.title`, `tag`))
                if rule.start_sufficient:
                    item = rule.filter_tag(tag, attrs)
                    filtered = "True"
                    # give'em a chance to replace more than one attribute
                    if item[0]==STARTTAG and item[1]==tag:
                        foo,tag,attrs = item
                        continue
                    else:
                        break
                else:
                    debug(NIGHTMARE, "HtmlFilter: put on buffer")
                    rulelist.append(rule)
        if rulelist:
            # remember buffer position for end tag matching
            pos = len(self.buf)
            self.rulestack.append((pos, rulelist))
        if filtered:
            self.buf_append_data(item)
        elif self.javascript:
            # if its not yet filtered, try filter javascript
            self.jsStartElement(tag, attrs)
        else:
            self.buf.append(item)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and not self.javascript:
            self.buf2data()


    def endElement (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the buffer (by calling buf2data)"""
        item = [ENDTAG, tag]
        if self.state=='wait':
            return self.waitbuf.append(item)
        filtered = 0
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag):
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.buf):
                    rule.filter_complete(pos, self.buf)
                    filtered = "True"
                    break
        if not filtered:
            if self.javascript and tag=='script' and \
               self.jsEndElement(tag):
                del self.buf[-1]
                del self.buf[-1]
            else:
                self.buf.append(item)
        if not self.rulestack:
            self.buf2data()


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
        elif tag=='script':
            lang = attrs.get('language', '').lower()
            url = attrs.get('src', '')
            scrtype = attrs.get('type', '').lower()
            is_js = scrtype=='text/javascript' or \
                    lang.startswith('javascript') or \
                    not (lang or scrtype)
            if is_js and url:
                return self.jsScriptSrc(url, lang)
        self.buf.append([STARTTAG, tag, attrs])


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
        debug(HURT_ME_PLENTY, "JS: jsForm", `name`, `action`, `target`)
        self.jsEnv.addForm(name, action, target)


    def jsScriptData (self, data, url, ver):
        assert self.state=='wait'
        if data is None:
            if not self.script:
                print >> sys.stderr, "empty JS src", url
            else:
                self.buf.append([STARTTAG, "script", {'type':
                                                      'text/javascript'}])
                self.buf.append([DATA, "<!--\n%s\n//-->"%self.script])
            self.state = 'parse'
            self.script = ''
            debug(NIGHTMARE, "Filter: switching back to parse with")
            debug(NIGHTMARE, "Filter: self.buf", `self.buf`)
            debug(NIGHTMARE, "Filter: self.waitbuf", `self.waitbuf`)
            debug(NIGHTMARE, "Filter: self.inbuf", `self.inbuf.getvalue()`)
        else:
            debug(HURT_ME_PLENTY, "JS: read", len(data), "<=", url)
            self.script += data


    def jsScriptSrc (self, url, language):
        assert self.state=='parse'
        ver = 0.0
        if language:
            mo = re.search(r'(?i)javascript(?P<num>\d\.\d)', language)
            if mo:
                ver = float(mo.group('num'))
        url = urlparse.urljoin(self.url, url)
        debug(HURT_ME_PLENTY, "JS: jsScriptSrc", url, ver)
        self.state = 'wait'
        client = HttpProxyClient(self.jsScriptData, (url, ver))
        ClientServerMatchmaker(client,
                               "GET %s HTTP/1.1" % url, #request
                               {}, #headers
                               '', #content
                               {'nofilter': None},
                               'identity', # compress
                               )
        self.waited = "True"


    def jsScript (self, script, ver):
        """execute given script with javascript version ver
           return True if the script generates any output, else False"""
        #debug(NIGHTMARE, "JS: jsScript", ver, `script`)
        self.output_counter = 0
        self.jsEnv.attachListener(self)
        self.jsfilter = HtmlFilter(self.rules, self.url,
                 comments=self.comments, javascript=self.javascript)
        self.jsEnv.executeScript(script, ver)
        self.jsEnv.detachListener(self)
        if self.output_counter:
            self.jsfilter.flush()
            self.outbuf.write(self.jsfilter.flushbuf())
            self.buf[-2:-2] = self.jsfilter.buf
            self.rulestack += self.jsfilter.rulestack
        self.jsfilter = None
        return self.popup_counter + self.output_counter


    def processData (self, data):
        # parse recursively
        self.output_counter += 1
        self.jsfilter.feed(data)


    def processPopup (self):
        self.popup_counter += 1


    def jsEndElement (self, tag):
        """parse generated html for scripts
           return True if the script generates any output, else False"""
        if len(self.buf)<2:
            return
        if self.buf[-1][0]!=DATA:
            # <script></script>
            return
        script = self.buf[-1][1].strip()
        if not (self.buf[-2][0]==STARTTAG and \
                self.buf[-2][1]=='script'):
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


    def errorfun (self, msg, name):
        print >> sys.stderr, name, "parsing %s: %s" % (self.url, msg)

    def _error (self, msg):
        self.errorfun(msg, "error")

    def _warning (self, msg):
        self.errorfun(msg, "warning")

    def _fatalError (self, msg):
        self.errorfun(msg, "fatalError")
