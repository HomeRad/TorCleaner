"""filter a HTML stream."""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import re, urlparse, wc
from cStringIO import StringIO
from wc.parser.htmllib import HtmlParser
from wc.parser import resolve_html_entities, strip_quotes
from wc.filter import FilterWait, FilterPics
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc.filter.PICS import check_pics
from wc.log import *
# JS imports
from wc.js.JSListener import JSListener
from wc.js import escape_js, unescape_js
try:
   from wc.js import jslib
except ImportError:
    jslib = None
from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
from wc.proxy.HttpProxyClient import HttpProxyClient
from wc.proxy import make_timer
from HtmlTags import check_spelling

# whitespace matcher
_has_ws = re.compile("\s").search

_start_js_comment = re.compile(r"^<!--\s*").search
_end_js_comment = re.compile(r"\s*-->$").search

class JSHtmlListener (JSListener):
    """defines callback handlers for Javascript code"""
    def __init__ (self, opts):
        self.js_filter = opts['javascript'] and jslib
        self.js_html = None
        self.js_src = False
        self.js_script = ''
        if self.js_filter:
            self.js_env = jslib.new_jsenv()
            self.js_output = 0
            self.js_popup = 0


    def jsProcessData (self, data):
        """process data produced by document.write() JavaScript"""
        self._debug("JS document.write %s", `data`)
        self.js_output += 1
        # parse recursively
        self.js_html.feed(data)


    def jsProcessPopup (self):
        """process javascript popup"""
        self._debug("JS: popup")
        self.js_popup += 1


    def jsProcessError (self, msg):
        """process javascript syntax error"""
        error(FILTER, "JS error at %s", self.url)
        error(FILTER, msg)


class BufferHtmlParser (HtmlParser):
    """Define error functions for HTML parsing and two buffers:
         self.buf - list of parsed HTML tags
         self.outbuf - StringIO with already filtered HTML data
    """
    def __init__ (self):
        HtmlParser.__init__(self)
        if wc.config['showerrors']:
            self.error = self._error
            self.warning = self._warning
            self.fatalError = self._fatalError
        self.outbuf = StringIO()
        self.buf = []


    def buf_append_data (self, data):
        """we have to make sure that we have no two following
        DATA things in the tag buffer. Why? To be 100% sure that
        an ENCLOSED match really matches enclosed data.
        """
        self._debug("buf_append_data")
        if data[0]==DATA and self.buf and self.buf[-1][0]==DATA:
            self.buf[-1][1] += data[1]
        else:
            self.buf.append(data)


    def flushbuf (self):
        """clear and return the output buffer"""
        self._debug("flushbuf")
        data = self.outbuf.getvalue()
        self.outbuf.close()
        self.outbuf = StringIO()
        return data


    def buf2data (self):
        """Append all tags of the tag buffer to the output buffer"""
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


    def _error (self, msg):
        """signal a filter/parser error"""
        error(PARSER, msg)

    def _warning (self, msg):
        """signal a filter/parser warning"""
        warn(PARSER, msg)

    def _fatalError (self, msg):
        """signal a fatal filter/parser error"""
        critical(PARSER, msg)



class FilterHtmlParser (BufferHtmlParser, JSHtmlListener):
    """This parser has filter rules, data buffers and a rule stack.
       XXX fixme: should make internal functions start with _
       States:
       parse => default parsing state, no background fetching
       wait  => this filter (or a recursive HtmlParser used by javascript)
                is fetching additionally data in the background.
                Flushing data in wait state raises a FilterWait
                When finished for <script src="">, the buffers look like
                this:
                fed data chunks (example):
                        [------------------][-------][----------][--...
                outbuf: [--]
                buf:        [-----]
                waitbuf:           [-------]
                inbuf:                      [-------------- ...
                                   ^-- <script src> tag

                When finished with script data, the buffers look like
                XXX (to be done)

       After a wait state, replays the waitbuf and re-feed the inbuf
       data.
    """

    def __init__ (self, rules, pics, url, **opts):
        "init rules and buffers"
        BufferHtmlParser.__init__(self)
        JSHtmlListener.__init__(self, opts)
        self.rules = rules
        self.pics = pics
        self.comments = opts['comments']
        self.level = opts.get('level', 0)
        self.state = ('parse',)
        self.waited = 0
        self.rulestack = []
        self.inbuf = StringIO()
        self.waitbuf = []
        self.url = url or "unknown"
        self.base_url = None


    def __repr__ (self):
        """representation with recursion level and state"""
        return "<HtmlParser[%d] %s>" % (self.level, str(self.state))


    def _debug (self, msg, *args):
        """debug with recursion level and state"""
        debug(FILTER, "HtmlParser[%d,%s]: %s"%\
              (self.level, self.state[0], msg), *args)


    def _debugbuf (self):
        """print debugging information about data buffer status"""
        self._debug("self.outbuf %s", `self.outbuf.getvalue()`)
        self._debug("self.buf %s", `self.buf`)
        self._debug("self.waitbuf %s", `self.waitbuf`)
        self._debug("self.inbuf %s", `self.inbuf.getvalue()`)


    def feed (self, data):
        """feed some data to the parser"""
        if self.state[0]=='parse':
            # look if we must replay something
            if self.waited > 0:
                self.waited = 0
                waitbuf, self.waitbuf = self.waitbuf, []
                self.replay(waitbuf)
                if self.state[0]!='parse':
                    self.inbuf.write(data)
                    return
                data = self.inbuf.getvalue() + data
                self.inbuf.close()
                self.inbuf = StringIO()
            if data:
                # only feed non-empty data
                self._debug("feed %s", `data`)
                self.parser.feed(data)
            else:
                self._debug("feed")
                pass
        else:
            # wait state ==> put in input buffer
            self._debug("wait")
            self.inbuf.write(data)


    def flush (self):
        self._debug("flush")
        # flushing in wait state raises a filter exception
        if self.waited > 100:
            error(FILTER, "Waited too long for %s"%self.state[1])
        elif self.state[0]=='wait':
            self.waited += 1
            raise FilterWait("HtmlParser[%d,wait]: waited %d times for %s"%\
                             (self.level, self.waited, self.state[1]))
        self.parser.flush()


    def replay (self, waitbuf):
        """call the handler functions again with buffer data"""
        self._debug("replay %s", `waitbuf`)
        for item in waitbuf:
            if item[0]==DATA:
                self._data(item[1])
            elif item[0]==STARTTAG:
                self.startElement(item[1], item[2])
            elif item[0]==ENDTAG:
                self.endElement(item[1])
            elif item[0]==COMMENT:
                self.comment(item[1])


    def _data (self, d):
        """general handler for data"""
        item = [DATA, d]
        if self.state[0]=='wait':
            return self.waitbuf.append(item)
        self.buf_append_data(item)


    def buf2data (self):
        """dont write any data to buf if there are still pics rules"""
        if self.pics:
            return
        BufferHtmlParser.buf2data(self)


    def cdata (self, data):
        """character data"""
        self._debug("cdata %s", `data`)
        return self._data(data)


    def characters (self, data):
        """characters"""
        self._debug("characters %s", `data`)
        return self._data(data)


    def comment (self, data):
        """a comment; accept only non-empty comments"""
        self._debug("comment %s", `data`)
        item = [COMMENT, data]
        if self.state[0]=='wait':
            return self.waitbuf.append(item)
        if self.comments and data:
            self.buf.append(item)


    def doctype (self, data):
        self._debug("doctype %s", `data`)
        return self._data("<!DOCTYPE%s>"%data)


    def pi (self, data):
        self._debug("pi %s", `data`)
        return self._data("<?%s?>"%data)


    def startElement (self, tag, attrs):
        """We get a new start tag. New rules could be appended to the
        pending rules. No rules can be removed from the list."""
        # default data
        self._debug("startElement %s", `tag`)
        tag = check_spelling(tag, self.url)
        item = [STARTTAG, tag, attrs]
        if self.state[0]=='wait':
            return self.waitbuf.append(item)
        rulelist = []
        filtered = False
        if tag=="meta" and \
           attrs.get('http-equiv', '').lower() =='pics-label':
            labels = resolve_html_entities(attrs.get('content', ''))
            # note: if there are no pics rules, this loop is empty
            for rule in self.pics:
                msg = check_pics(rule, labels)
                if msg:
                    raise FilterPics(msg)
            # first labels match counts
            self.pics = []
        elif tag=="body":
            # headers finished
            if self.pics:
                # no pics data found
                self.pics = []
        elif tag=="base" and attrs.has_key('href'):
            self.base_url = strip_quotes(attrs['href'])
            self._debug("using base url %s", `self.base_url`)
        elif tag=="input" and attrs.has_key('type'):
            # fix IE crash bug on empty type attribute
            if not attrs['type']:
                del attrs['type']
        elif tag=="fieldset" and attrs.has_key('style'):
            # fix Mozilla crash bug on fieldsets
            if "position" in attrs['style']:
                del attrs['style']
        # look for filter rules which apply
        for rule in self.rules:
            if rule.match_tag(tag) and rule.match_attrs(attrs):
                self._debug("matched rule %s on tag %s", `rule.title`, `tag`)
                if rule.start_sufficient:
                    item = rule.filter_tag(tag, attrs)
                    filtered = True
                    if item[0]==STARTTAG and item[1]==tag:
                        foo,tag,attrs = item
                        # give'em a chance to replace more than one attribute
                        continue
                    else:
                        break
                else:
                    self._debug("put on buffer")
                    rulelist.append(rule)
        if rulelist:
            # remember buffer position for end tag matching
            pos = len(self.buf)
            self.rulestack.append((pos, rulelist))
        if filtered:
            self.buf_append_data(item)
        elif self.js_filter:
            # if its not yet filtered, try filter javascript
            self.jsStartElement(tag, attrs)
        else:
            self.buf.append(item)
        # if rule stack is empty, write out the buffered data
        if not self.rulestack and not self.js_filter:
            self.buf2data()


    def endElement (self, tag):
        """We know the following: if a rule matches, it must be
        the one on the top of the stack. So we look only at the top
        rule.
	If it matches and the rule stack is now empty we can flush
	the buffer (by calling buf2data)"""
        self._debug("endElement %s", `tag`)
        tag = check_spelling(tag, self.url)
        item = [ENDTAG, tag]
        if self.state[0]=='wait':
            return self.waitbuf.append(item)
        if not self.filterEndElement(tag):
            if self.js_filter and tag=='script':
                self.jsEndElement(item)
                self.js_src = False
                return
            self.buf.append(item)
        if not self.rulestack:
            self.buf2data()


    def filterEndElement (self, tag):
        # remember: self.rulestack[-1][1] is the rulelist that
        # matched for a start tag. and if the first one ([0])
        # matches, all other match too
        if self.rulestack and self.rulestack[-1][1][0].match_tag(tag):
            pos, rulelist = self.rulestack.pop()
            for rule in rulelist:
                if rule.match_complete(pos, self.buf):
                    rule.filter_complete(pos, self.buf)
                    return True
        return False


    def jsStartElement (self, tag, attrs):
        """Check popups for onmouseout and onmouseover.
           Inline extern javascript sources"""
        changed = 0
        self.js_src = False
        self.js_output = 0
        self.js_popup = 0
        for name in ('onmouseover', 'onmouseout'):
            if attrs.has_key(name) and self.jsPopup(attrs, name):
                self._debug("JS: del %s from %s", `name`, `tag`)
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
        self._debug("JS: jsPopup")
        val = resolve_html_entities(attrs[name])
        if not val: return
        self.js_env.attachListener(self)
        try:
            self.js_env.executeScriptAsFunction(val, 0.0)
        except jslib.error, msg:
            pass
        self.js_env.detachListener(self)
        res = self.js_popup
        self.js_popup = 0
        return res


    def jsForm (self, name, action, target):
        """when hitting a (named) form, notify the JS engine about that"""
        if not name: return
        self._debug("jsForm %s action %s %s", `name`, `action`, `target`)
        self.js_env.addForm(name, action, target)


    def jsScriptData (self, data, url, ver):
        """Callback for loading <script src=""> data in the background
           If downloading is finished, data is None"""
        assert self.state[0]=='wait'
        if data is None:
            if not self.js_script:
                warn(PARSER, "HtmlParser[%d]: empty JS src %s", self.level, url)
            else:
                self.buf.append([STARTTAG, "script", {'type':
                                                      'text/javascript'}])
                script = "\n<!--\n%s\n//-->\n"%escape_js(self.js_script)
                self.buf.append([DATA, script])
                # Note: <script src=""> could be missing an end tag,
                # but now we need one. Look later for a duplicate </script>.
                self.buf.append([ENDTAG, "script"])
                self.js_script = ''
            self.state = ('parse',)
            self._debug("switching back to parse with")
            self._debugbuf()
        else:
            self._debug("JS read %d <= %s", len(data), url)
            self.js_script += data


    def jsScriptSrc (self, url, language):
        """Start a background download for <script src=""> tags"""
        assert self.state[0]=='parse'
        ver = 0.0
        if language:
            mo = re.search(r'(?i)javascript(?P<num>\d\.\d)', language)
            if mo:
                ver = float(mo.group('num'))
        if self.base_url:
            url = urlparse.urljoin(self.base_url, url)
        else:
            url = urlparse.urljoin(self.url, url)
        if _has_ws(url):
            warn(PARSER, "HtmlParser[%d]: broken JS url %s at %s", self.level,
                         `url`, `self.url`)
            return
        self.state = ('wait', url)
        self.waited = 1
        self.js_src = True
        client = HttpProxyClient(self.jsScriptData, (url, ver))
        ClientServerMatchmaker(client,
                               "GET %s HTTP/1.1" % url, #request
                               {}, #headers
                               '', #content
                               {'nofilter': None}, # nofilter
                               'identity', # compress
                               mime = "application/x-javascript",
                               )


    def jsScript (self, script, ver, item):
        """execute given script with javascript version ver"""
        self._debug("JS: jsScript %s %s", ver, `script`)
        assert self.state[0]=='parse'
        assert len(self.buf) >= 2
        self.js_output = 0
        self.js_env.attachListener(self)
        # start recursive html filter (used by jsProcessData)
        self.js_html = FilterHtmlParser(self.rules, self.pics, self.url,
       comments=self.comments, javascript=self.js_filter, level=self.level+1)
        # execute
        self.js_env.executeScript(unescape_js(script), ver)
        self.js_env.detachListener(self)
        # wait for recursive filter to finish
        self.jsEndScript(item)


    def jsEndScript (self, item):
        self._debug("JS: endScript")
        assert len(self.buf) >= 2
        if self.js_output:
            try:
                self.js_html.feed('')
                self.js_html.flush()
            except FilterWait:
                self.state = ('wait', 'recursive script')
                self.waited = 1
                make_timer(0.2, lambda : self.jsEndScript(item))
                return
            self.js_html._debugbuf()
            assert not self.js_html.inbuf.getvalue()
            assert not self.js_html.waitbuf
            assert len(self.buf) >= 2
            self.buf[-2:-2] = [[DATA, self.js_html.outbuf.getvalue()]]+self.js_html.buf
        self.js_html = None
        if (self.js_popup + self.js_output) > 0:
            # delete old script
            del self.buf[-1]
            del self.buf[-1]
        elif not self.filterEndElement(item[1]):
            self.buf.append(item)
        self._debug("JS: switching back to parse with")
        self._debugbuf()
        self.state = ('parse',)


    def jsEndElement (self, item):
        """parse generated html for scripts"""
        self._debug("jsEndElement buf %s", `self.buf`)
        if len(self.buf)<2:
            # syntax error, ignore
            return
        if self.js_src:
            del self.buf[-1]
            if len(self.buf)<2:
                # syntax error, ignore
                warn(PARSER, "JS end self.buf %s", str(self.buf))
                return
            if len(self.buf) > 2 and \
               self.buf[-3][0]==STARTTAG and self.buf[-3][1]=='script':
                del self.buf[-1]
        if len(self.buf)<2 or self.buf[-1][0]!=DATA or \
            self.buf[-2][0]!=STARTTAG or self.buf[-2][1]!='script':
            # syntax error, ignore
            return
        # get script data
        script = self.buf[-1][1].strip()
        # remove html comments
        mo = _start_js_comment(script)
        if mo:
            script = script[mo.end():]
        mo = _end_js_comment(script)
        if mo:
            script = script[:mo.start()]
        if not script:
            # again, ignore an empty script
            del self.buf[-1]
            del self.buf[-1]
            return
        # put correctly quoted script data into buffer
        self.buf[-1][1] = "\n<!--\n%s\n//-->\n"%escape_js(script)
        # execute script
        self.jsScript(script, 0.0, item)
