# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
Filter JavaScript.
"""

import re
import urlparse

import wc
import wc.HtmlParser
import wc.log
import wc.filter
import wc.filter.html.HtmlParser
import wc.url
import wc.proxy
import wc.proxy.ClientServerMatchmaker
import wc.proxy.HttpProxyClient
import wc.proxy.Headers
import wc.js
import wc.js.jslib
import wc.js.JSListener
import wc.decorators


_replace_ws = re.compile(ur"\s+").sub
js_event_attrs = (
    'onmouseover',
    'onmouseout',
    'onload',
    'onunload',
    'onselectstart',
)

class JSFilter (wc.js.JSListener.JSListener):
    """
    Defines callback handlers for filtering Javascript code.
    """

    def __init__ (self, url, localhost, opts):
        """
        Initialize javascript engine and variables.
        """
        # True if javascript has to be filtered
        self.javascript = opts['javascript']
        self.level = opts.get('level', 0)
        self.comments = opts['comments']
        self.jscomments = opts['jscomments']
        self.url = url or "unknown"
        self.localhost = localhost
        self.js_src = False
        self.js_script = u''
        # HttpProxyClient object used in background downloads,
        # has self.jsScriptData as handler
        self.js_client = None
        # gets set by parent parser
        self.htmlparser = None
        # HtmlParser used in background downloads
        self.js_htmlparser = None
        if self.javascript:
            self.js_env = wc.js.jslib.JSEnv()
            #self.js_env.setBrowser(opts['browser'])
            self.js_output = 0
            self.js_popup = 0

    def _str__ (self):
        """
        Info string with class name and recursion level.
        """
        return "%s[%d]" % (self.__class__.__name__, self.level)

    def js_process_data (self, data):
        """
        Process data produced by document.write() JavaScript.
        """
        assert wc.log.debug(wc.LOG_JS, "%s js_process_data %r", self, data)
        self.js_output += 1
        # parse recursively
        self.js_htmlparser.feed(data)

    def js_process_popup (self):
        """
        Process javascript popup.
        """
        assert wc.log.debug(wc.LOG_JS, "%s js_process_popup", self)
        self.js_popup += 1

    def js_process_error (self, msg):
        """
        Process javascript syntax error.
        """
        assert wc.log.debug(wc.LOG_JS, "JS error at %s", self.url)
        assert wc.log.debug(wc.LOG_JS, msg.rstrip())

    def jsPopup (self, attrs, name):
        """
        Check if attrs[name] javascript opens a popup window.
        """
        assert wc.log.debug(wc.LOG_JS, "%s jsPopup %r", self, attrs[name])
        val = wc.HtmlParser.resolve_html_entities(attrs[name])
        if not val:
            return
        self.js_env.listeners.append(self)
        val = val.encode(self.htmlparser.encoding)
        try:
            self.js_env.executeScriptAsFunction(val, 0.0)
        except wc.js.jslib.error:
            pass
        self.js_env.listeners.remove(self)
        res, self.js_popup = self.js_popup, 0
        return res

    def new_instance (self, **opts):
        """
        Generate new JSFilter instance.
        """
        return JSFilter(self.url, self.localhost, opts)

    def jsScript (self, script, ver, item):
        """
        Execute script with javascript a specific version.

        @param script: the javascript script
        @type script: string
        @param ver: javascript version
        @type ver: float
        """
        assert wc.log.debug(wc.LOG_JS, "%s jsScript %s %r", self, ver, script)
        assert self.htmlparser.state[0] == 'parse', \
               "parser %s not in parse state" % self.htmlparser
        assert len(self.htmlparser.tagbuf) >= 2, \
               "parser %s must have script start and " \
               "content tags in tag buffer" % self.htmlparser
        self.js_output = 0
        self.js_env.listeners.append(self)
        # start recursive html filter (used by js_process_data)
        handler = self.new_instance(comments=self.comments,
            jscomments=self.jscomments,
            javascript=self.javascript, level=self.level+1)
        self.js_htmlparser = wc.filter.html.HtmlParser.HtmlParser(handler)
        handler.htmlparser = self.js_htmlparser
        # encode for JS engine
        script = script.encode(self.htmlparser.encoding)
        # execute
        self.js_env.executeScript(script, ver)
        self.js_env.listeners.remove(self)
        # wait for recursive filter to finish
        self.js_end_script(item)

    def js_end_script (self, item):
        """
        A </script> was encountered.
        """
        assert wc.log.debug(wc.LOG_JS, "%s js_end_script %s", self, item)
        self.htmlparser.debugbuf(cat=wc.LOG_JS)
        if len(self.htmlparser.tagbuf) < 2:
            assert False, "parser %s must have script start and content " \
                          "tags in tag buffer" % self.htmlparser
        if self.js_output:
            try:
                self.js_htmlparser.feed('')
                self.js_htmlparser.flush()
            except wc.filter.FilterWait:
                assert wc.log.debug(wc.LOG_JS,
                                    "%s JS subprocessor is waiting", self)
                self.htmlparser.state = ('wait', 'recursive script')
                self.htmlparser.waited = 1
                wc.proxy.make_timer(1, lambda: self.js_end_script(item))
                return
            self.js_htmlparser.debugbuf(cat=wc.LOG_JS)
            assert not self.js_htmlparser.inbuf.getvalue()
            assert not self.js_htmlparser.waitbuf
            assert len(self.htmlparser.tagbuf) >= 2, \
                   "too small buffer %s" % self.htmlparser.tagbuf
            data = unicode(self.js_htmlparser.getoutput(),
                           self.js_htmlparser.encoding)
            self.htmlparser.tagbuf[-2:-2] = \
                   [[wc.filter.html.DATA, data]] + self.js_htmlparser.tagbuf
            self.htmlparser.debugbuf(cat=wc.LOG_JS)
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
        elif not self.filter_end_element(item[1]):
            self.htmlparser.tagbuf.append(item)
        self.htmlparser.state = ('parse',)
        assert wc.log.debug(wc.LOG_JS,
                            "%s switching back to parse with", self)
        self.htmlparser.debugbuf(cat=wc.LOG_JS)

    @wc.decorators.notimplemented
    def filter_end_element (self, tag):
        """
        Filters an end tag, return True if tag was filtered, else False.
        """
        pass

    def js_end_element (self, item):
        """
        Parse generated html for scripts.
        """
        assert wc.log.debug(wc.LOG_JS,
                     "%s js_end_element buf %r", self, self.htmlparser.tagbuf)
        if len(self.htmlparser.tagbuf) < 2:
            # syntax error, ignore
            assert wc.log.debug(wc.LOG_JS,
                    "JS syntax error, self.tagbuf %r", self.htmlparser.tagbuf)
            return
        if self.js_src:
            assert wc.log.debug(wc.LOG_JS,
                         "JS src, self.tagbuf %r", self.htmlparser.tagbuf)
            del self.htmlparser.tagbuf[-1]
            if len(self.htmlparser.tagbuf) < 2:
                # syntax error, ignore
                wc.log.warn(wc.LOG_JS,
                            "JS end, self.tagbuf %s", self.htmlparser.tagbuf)
                return
            if len(self.htmlparser.tagbuf) > 2 and \
               self.htmlparser.tagbuf[-3][0] == \
               wc.filter.html.STARTTAG and \
               self.htmlparser.tagbuf[-3][1] == 'script':
                del self.htmlparser.tagbuf[-1]
        if len(self.htmlparser.tagbuf) < 2 or \
           self.htmlparser.tagbuf[-1][0] != wc.filter.html.DATA or \
           self.htmlparser.tagbuf[-2][0] != wc.filter.html.STARTTAG or \
           self.htmlparser.tagbuf[-2][1] != 'script':
            # syntax error, ignore
            return
        js_ok, js_lang = wc.js.get_js_data(self.htmlparser.tagbuf[-2][2])
        if not js_ok:
            # no JavaScript, add end tag and ignore
            self.htmlparser.tagbuf.append(item)
            return
        ver = wc.js.get_js_ver(js_lang)
        # get script data
        script = self.htmlparser.tagbuf[-1][1].strip()
        # remove html comments
        script = wc.js.remove_html_comments(script)
        if not script:
            # Delete empty script without src attribute.
            attrs = self.htmlparser.tagbuf[-2][2]
            if not attrs.get("src"):
                del self.htmlparser.tagbuf[-1]
                del self.htmlparser.tagbuf[-1]
            return
        # put correctly quoted script data into buffer
        script = wc.js.clean(script, jscomments=self.jscomments)
        self.htmlparser.tagbuf[-1][1] = script
        # execute script
        self.jsScript(script, ver, item)

    def js_start_element (self, tag, attrs, starttype):
        """
        Check popups for onmouseout and onmouseover.
        Inline extern javascript sources.
        """
        assert wc.log.debug(wc.LOG_JS, "%s js_start_element", self)
        self.js_src = False
        self.js_output = 0
        self.js_popup = 0
        for name in js_event_attrs:
            if attrs.has_key(name) and self.jsPopup(attrs, name):
                assert wc.log.debug(wc.LOG_JS,
                                    "JS: del %r from %r", name, tag)
                del attrs[name]
        if tag == 'form':
            name = attrs.get_true('name', attrs.get_true('id', u""))
            self.jsForm(name, attrs.get('action', u''),
                        attrs.get_true('target', u''))
        elif tag == 'script':
            js_ok, js_lang = wc.js.get_js_data(attrs)
            url = attrs.get_true('src', u"")
            if url:
                # sanitize script src url
                url = _replace_ws(u'', url)
                url = wc.HtmlParser.resolve_html_entities(url)
                # some urls are relative, need to make absolut
                if self.base_url:
                    url = urlparse.urljoin(self.base_url, url)
                else:
                    url = urlparse.urljoin(self.url, url)
                # XXX TODO: support https background downloads
                if js_ok and wc.url.url_is_absolute(url) and \
                   not url.startswith("https"):
                    self.jsScriptSrc(url, js_lang)
                    return
        self.htmlparser.tagbuf.append([starttype, tag, attrs])

    def jsForm (self, name, action, target):
        """
        When hitting a named form, add it to the JS environment.
        """
        if not name:
            return
        assert wc.log.debug(wc.LOG_JS, "%s jsForm %r action %r %r",
                     self, name, action, target)
        name = name.encode(self.htmlparser.encoding)
        action = action.encode(self.htmlparser.encoding)
        target = target.encode(self.htmlparser.encoding)
        self.js_env.addForm(name, action, target)

    def jsScriptSrc (self, url, language):
        """
        Start a background download for <script src=""> tags.
        After that, self.js_client points to the proxy client object.
        """
        assert wc.log.debug(wc.LOG_JS, "%s jsScriptSrc %r", self, url)
        assert self.htmlparser.state[0] == 'parse', \
               "non-parse state %s" % self.htmlparser.state
        ver = wc.js.get_js_ver(language)
        if not wc.js.is_safe_js_url(self.url, url):
            wc.log.warn(wc.LOG_JS,
                        "invalid script src url %r at %s (base %r)",
                        url, self.url, self.base_url)
            # returning here will look like a syntax error
            return
        self.htmlparser.state = ('wait', url)
        self.htmlparser.waited = 1
        self.js_src = True
        self.js_client = wc.proxy.HttpProxyClient.HttpProxyClient(
                               self.jsScriptData, (url, ver), self.localhost)
        headers = wc.proxy.Headers.get_wc_client_headers(
                                             self.js_client.hostname)
        # note: some javascript servers do not specify content encoding
        # so only accept non-encoded content here
        headers['Accept-Encoding'] = 'identity\r'
        wc.proxy.ClientServerMatchmaker.ClientServerMatchmaker(self.js_client,
            self.js_client.request, headers,
            '', # content
            mime_types=["application/x-javascript", "text/javascript"],
            )

    def jsScriptData (self, data, url, ver):
        """
        Callback for loading <script src=""> data in the background
        If downloading is finished, data is None.
        """
        assert self.htmlparser.state[0] == 'wait', \
            "non-wait state in %s" % self.htmlparser
        assert wc.log.debug(wc.LOG_JS, "%s jsScriptData %r", self, data)
        if data is None:
            if not self.js_script:
                wc.log.warn(wc.LOG_JS, "empty JavaScript src %s", url)
                msg = _("error fetching script from %r") % url
                self.js_script = u"// " + msg
            else:
                msg = _("fetched script from %r") % url
            item = [wc.filter.html.COMMENT, u" %s " % msg]
            self.htmlparser.tagbuf.append(item)
            self.htmlparser.tagbuf.append([wc.filter.html.DATA, u"\n"])
            d = wc.containers.ListDict()
            d[u'type'] = u'text/javascript'
            item = [wc.filter.html.STARTTAG, u"script", d]
            self.htmlparser.tagbuf.append(item)
            # norm html comments
            script = wc.js.clean(self.js_script, jscomments=self.jscomments)
            self.htmlparser.tagbuf.append(
                                   [wc.filter.html.DATA, script])
            # Note: <script src=""> could be missing an end tag,
            # but now we need one. Look later for a duplicate </script>.
            self.htmlparser.tagbuf.append([wc.filter.html.ENDTAG, u"script"])
            self.js_script = u''
            self.htmlparser.state = ('parse',)
            assert wc.log.debug(wc.LOG_JS,
                                "%s switching back to parse with", self)
            self.htmlparser.debugbuf(cat=wc.LOG_JS)
        else:
            assert wc.log.debug(wc.LOG_JS, "JS read %d <= %s", len(data), url)
            self.js_script += data.decode(self.htmlparser.encoding, "ignore")

    def finish (self):
        """
        Stop all background downloads immediately.
        """
        assert wc.log.debug(wc.LOG_JS, "%s finish", self)
        self.js_client.finish()
        self.js_client = None
        if self.js_htmlparser is not None:
            self.js_htmlparser.handler.finish()
            self.js_htmlparser = None
