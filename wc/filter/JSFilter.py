# -*- coding: iso-8859-1 -*-
"""filter JavaScript."""
# Copyright (C) 2000-2004  Bastian Kleineidam
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
from wc.parser import resolve_html_entities
from wc.filter import FilterWait
from wc.filter.HtmlParser import HtmlParser
from wc.filter.rules.RewriteRule import STARTTAG, ENDTAG, DATA, COMMENT
from wc.log import *
from wc.js.JSListener import JSListener
from wc.js import escape_js, unescape_js, get_js_ver, get_js_data, jslib
from wc.proxy.ClientServerMatchmaker import ClientServerMatchmaker
from wc.proxy.HttpProxyClient import HttpProxyClient
from wc.proxy.Headers import get_wc_client_headers
from wc.proxy import make_timer
from wc.url import url_norm, url_quote, stripsite

_start_js_comment = re.compile(r"^<!--([^\r\n]+)?").search
_end_js_comment = re.compile(r"\s*//[^\r\n]*-->$").search


class JSFilter (JSListener):
    """defines callback handlers for filtering Javascript code"""
    def __init__ (self, url, opts):
        # True if javascript has to be filtered
        self.javascript = opts['javascript']
        self.level = opts.get('level', 0)
        self.comments = opts['comments']
        self.url = url or "unknown"
        self.js_src = False
        self.js_script = ''
        # HttpProxyClient object used in background downloads,
        # has self.jsScriptData as handler
        self.js_client = None
        # HtmlParser used in background downloads
        self.js_htmlparser = None
        if self.javascript:
            self.js_env = jslib.JSEnv()
            self.js_output = 0
            self.js_popup = 0


    def _str__ (self):
        return "%s[%d]" % (self.__class__.__name__, self.level)


    def jsProcessData (self, data):
        """process data produced by document.write() JavaScript"""
        debug(FILTER, "%s jsProcessData %r", self, data)
        self.js_output += 1
        # parse recursively
        self.js_htmlparser.feed(data)


    def jsProcessPopup (self):
        """process javascript popup"""
        debug(FILTER, "%s jsProcessPopup", self)
        self.js_popup += 1


    def jsProcessError (self, msg):
        """process javascript syntax error"""
        error(FILTER, "JS error at %s", self.url)
        error(FILTER, msg)


    def jsPopup (self, attrs, name):
        """check if attrs[name] javascript opens a popup window"""
        debug(FILTER, "%s jsPopup", self)
        val = resolve_html_entities(attrs[name])
        if not val: return
        self.js_env.listeners.append(self)
        try:
            self.js_env.executeScriptAsFunction(val, 0.0)
        except jslib.error:
            pass
        self.js_env.listeners.remove(self)
        res, self.js_popup = self.js_popup, 0
        return res


    def new_instance (self, **opts):
        JSFilter(self.url, **opts)


    def jsScript (self, script, ver, item):
        """execute given script with javascript version ver"""
        debug(FILTER, "%s jsScript %s %r", self, ver, script)
        assert self.htmlparser.state[0]=='parse', "parser %s not in parse state" % self.htmlparser
        assert len(self.htmlparser.tagbuf) >= 2, "parser %s must have script start and content tags in tag buffer" % self.htmlparser
        self.js_output = 0
        self.js_env.listeners.append(self)
        # start recursive html filter (used by jsProcessData)
        handler = self.new_instance(comments=self.comments,
            javascript=self.javascript, level=self.level+1)
        self.js_htmlparser = HtmlParser(handler)
        handler.htmlparser = self.js_htmlparser
        # execute
        self.js_env.executeScript(unescape_js(script), ver)
        self.js_env.listeners.remove(self)
        # wait for recursive filter to finish
        self.jsEndScript(item)


    def jsEndScript (self, item):
        debug(FILTER, "%s jsEndScript %s", self, item)
        self.htmlparser.debugbuf()
        if len(self.htmlparser.tagbuf) < 2:
            assert False, "parser %s must have script start and content tags in tag buffer" % self.htmlparser
        if self.js_output:
            try:
                self.js_htmlparser.feed('')
                self.js_htmlparser.flush()
            except FilterWait:
                debug(FILTER, "%s JS subprocessor is waiting", self)
                self.htmlparser.state = ('wait', 'recursive script')
                self.htmlparser.waited = 1
                make_timer(0.2, lambda : self.jsEndScript(item))
                return
            self.js_htmlparser.debugbuf()
            assert not self.js_htmlparser.inbuf.getvalue()
            assert not self.js_htmlparser.waitbuf
            assert len(self.htmlparser.tagbuf) >= 2, "too small buffer %s" % self.htmlparser.tagbuf
            data = self.js_htmlparser.getoutput()
            self.htmlparser.tagbuf[-2:-2] = [[DATA, data]]+self.js_htmlparser.tagbuf
            self.htmlparser.debugbuf()
        self.js_htmlparser = None
        if self.js_popup or self.js_output:
            # either the javascript part popped up some windows or
            # it wrote something with document.write()
            # in both cases the javascript is deleted
            # This could potentially delete too much as there might be
            # valid JS functions defined that get used by other scripts.
            # In this case use an exception url in the Javascript filter
            # rule.
            del self.htmlparser.tagbuf[-1]
            del self.htmlparser.tagbuf[-1]
        elif not self.filterEndElement(item[1]):
            self.htmlparser.tagbuf.append(item)
        debug(FILTER, "%s switching back to parse with", self)
        self.htmlparser.debugbuf()
        self.htmlparser.state = ('parse',)


    def filterEndElement (self, tag):
        """filters an end tag, return True if tag was filtered, else False"""
        raise NotImplementError("Must be overridden in subclass")


    def jsEndElement (self, item):
        """parse generated html for scripts"""
        debug(FILTER, "%s jsEndElement buf %r", self, self.htmlparser.tagbuf)
        if len(self.htmlparser.tagbuf)<2:
            # syntax error, ignore
            warn(FILTER, "JS syntax error, self.tagbuf %r", self.htmlparser.tagbuf)
            return
        if self.js_src:
            debug(FILTER, "JS src, self.tagbuf %r", self.htmlparser.tagbuf)
            del self.htmlparser.tagbuf[-1]
            if len(self.htmlparser.tagbuf)<2:
                # syntax error, ignore
                warn(FILTER, "JS end, self.tagbuf %s", self.htmlparser.tagbuf)
                return
            if len(self.htmlparser.tagbuf) > 2 and \
               self.htmlparser.tagbuf[-3][0]==STARTTAG and \
               self.htmlparser.tagbuf[-3][1]=='script':
                del self.htmlparser.tagbuf[-1]
        if len(self.htmlparser.tagbuf)<2 or \
           self.htmlparser.tagbuf[-1][0]!=DATA or \
           self.htmlparser.tagbuf[-2][0]!=STARTTAG or \
           self.htmlparser.tagbuf[-2][1]!='script':
            # syntax error, ignore
            return
        js_ok, js_lang = get_js_data(self.htmlparser.tagbuf[-2][2])
        if not js_ok:
            # no JavaScript, add end tag and ignore
            self.htmlparser.tagbuf.append(item)
            return
        ver = get_js_ver(js_lang)
        # get script data
        script = self.htmlparser.tagbuf[-1][1].strip()
        # remove html comments
        mo = _start_js_comment(script)
        if mo:
            script = script[mo.end():]
        mo = _end_js_comment(script)
        if mo:
            script = script[:mo.start()]
        script = script.strip()
        if not script:
            # again, ignore an empty script
            del self.htmlparser.tagbuf[-1]
            del self.htmlparser.tagbuf[-1]
            return
        # put correctly quoted script data into buffer
        self.htmlparser.tagbuf[-1][1] = "\n<!--\n%s\n//-->\n"%escape_js(script)
        # execute script
        self.jsScript(script, ver, item)


    def jsStartElement (self, tag, attrs):
        """Check popups for onmouseout and onmouseover.
           Inline extern javascript sources"""
        debug(FILTER, "%s jsStartElement", self)
        self.js_src = False
        self.js_output = 0
        self.js_popup = 0
        for name in ('onmouseover', 'onmouseout'):
            if attrs.has_key(name) and self.jsPopup(attrs, name):
                debug(FILTER, "JS: del %r from %r", name, tag)
                del attrs[name]
        if tag=='form':
            name = attrs.get('name', attrs.get('id'))
            self.jsForm(name, attrs.get('action', ''), attrs.get('target', ''))
        elif tag=='script':
            js_ok, js_lang = get_js_data(attrs)
            url = attrs.get('src', '')
            if js_ok and url:
                self.jsScriptSrc(url, js_lang)
                return
        self.htmlparser.tagbuf.append([STARTTAG, tag, attrs])


    def jsForm (self, name, action, target):
        """when hitting a named form, add it to the JS environment"""
        if not name:
            return
        debug(FILTER, "%s jsForm %r action %r %r", self, name, action, target)
        self.js_env.addForm(name, action, target)


    def jsScriptSrc (self, url, language):
        """Start a background download for <script src=""> tags
           After that, self.js_client points to the proxy client object"""
        debug(FILTER, "%s jsScriptSrc %r", self, url)
        assert self.htmlparser.state[0]=='parse', "non-parse state %s" % self.htmlparser.state
        ver = get_js_ver(language)
        if self.base_url:
            url = urlparse.urljoin(self.base_url, url)
        else:
            url = urlparse.urljoin(self.url, url)
        # unquote and norm
        url = url_norm(url)
        host = stripsite(url)[0]
        if not host:
            error(FILTER, "invalid script src url %r at %s (base %r)", url, self.url, self.base_url)
            return
        self.htmlparser.state = ('wait', url)
        self.htmlparser.waited = 1
        self.js_src = True
        self.js_client = HttpProxyClient(self.jsScriptData, (url, ver))
        headers = get_wc_client_headers(host)
        # note: some javascript servers do not specify content encoding
        # so only accept non-encoded content here
        headers['Accept-Encoding'] = 'identity\r'
        ClientServerMatchmaker(self.js_client,
                               "GET %s HTTP/1.0" % url_quote(url), # request
                               headers,
                               '', # content
                               mime="application/x-javascript",
                               )


    def jsScriptData (self, data, url, ver):
        """Callback for loading <script src=""> data in the background
           If downloading is finished, data is None"""
        assert self.htmlparser.state[0]=='wait', "non-wait state"
        debug(FILTER, "%s jsScriptData %r", self, data)
        if data is None:
            if not self.js_script:
                warn(FILTER, "empty JavaScript src %s", url)
                self.js_script = "// error fetching script from %r"%url
            self.htmlparser.tagbuf.append([STARTTAG, "script", {'type': 'text/javascript'}])
            script = "\n<!--\n%s\n//-->\n"%escape_js(self.js_script)
            self.htmlparser.tagbuf.append([DATA, script])
            # Note: <script src=""> could be missing an end tag,
            # but now we need one. Look later for a duplicate </script>.
            self.htmlparser.tagbuf.append([ENDTAG, "script"])
            self.js_script = ''
            self.htmlparser.state = ('parse',)
            debug(FILTER, "%s switching back to parse with", self)
            self.htmlparser.debugbuf()
        else:
            debug(FILTER, "JS read %d <= %s", len(data), url)
            self.js_script += data


    def finish (self):
        """stop all background downloads immediately"""
        debug(FILTER, "%s finish", self)
        self.js_client.finish()
        self.js_client = None
        if self.js_htmlparser is not None:
            self.js_htmlparser.handler.finish()
            self.js_htmlparser = None

