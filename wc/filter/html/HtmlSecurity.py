# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2005  Bastian Kleineidam
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
Filter some security flaws out of HTML tags.

WARNING: this is by no means a complete. Don't rely on this module
to catch all known security flaws!
If you think you found a HTML related security flaw that is not covered
by this module, you are encouraged to inform me with details.
"""

import os
import re
import urllib
import sys

import wc
import wc.log
import wc.url


def _has_lots_of_percents (url):
    """
    Return True iff url has more than 10 percent chars in a row.
    """
    if not url:
        return False
    return '%'*11 in url


class HtmlSecurity (object):
    """
    Scan and repair known security exploits in HTML start/end tags.
    """

    def __init__ (self):
        self.in_winhelp = False # inside object tag calling WinHelp
        # running on MacOS or MacOSX
        self.macintosh = os.name == 'mac' or \
              (os.name == 'posix' and sys.platform.startswith('darwin'))

    # scan methods

    def scan_start_tag (self, tag, attrs, htmlfilter):
        """
        Delegate to individual start tag handlers.
        """
        fun = "%s_start" % tag
        if hasattr(self, fun):
            getattr(self, fun)(attrs, htmlfilter)

    def scan_end_tag (self, tag):
        """
        Delegate to individual end tag handlers.
        """
        fun = "%s_end" % tag
        if hasattr(self, fun):
            getattr(self, fun)()

    # helper methods to check/sanitize values

    def _check_attr_size (self, attrs, name, htmlfilter, maxlen=4):
        """
        Sanitize too large values.
        """
        # Note that a maxlen of 4 is recommended to also allow
        # percentages like '100%'.
        if attrs.has_key(name):
            val = attrs[name]
            if len(val) > maxlen:
                msg = "%s %r\n Detected a too large %s attribute value"
                msg += " (length %d > %d)" % (len(val), maxlen)
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter, val, name)
                del attrs[name]

    def _check_javascript_url (self, attrs, name, htmlfilter):
        """
        Check if url has javascript: embedded.
        """
        if attrs.has_key(name):
            url = attrs[name].strip().lower()
            # to be sure catch all javascript: stuff
            if "javascript:" in url:
                msg = "%s\n Detected and prevented invlalid JS URL reference"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                del attrs[name]

    def _check_percent_url (self, attrs, name, htmlfilter):
        """
        Check if url has too much percent chars.
        """
        if attrs.has_key(name):
            url = attrs[name]
            if _has_lots_of_percents(url):
                # prevent CAN-2003-0870
                msg = "%s %r\n Detected and prevented Opera percent " \
                      "encoding overflow crash"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter, url)
                del attrs[name]

    # tag specific scan methods, sorted alphabetically

    def a_start (self, attrs, htmlfilter):
        """
        Check <a> start tag.
        """
        self._check_percent_url(attrs, 'href', htmlfilter)

    def body_start (self, attrs, htmlfilter):
        """
        Check <body> start tag.
        """
        if attrs.has_key('onload'):
            val = attrs['onload'].lower()
            pattern = r"window\s*\(\s*\)"
            if re.compile(pattern).search(val):
                del attrs['onload']
                msg = "%s\n Detected and prevented IE window() crash bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)

    def embed_start (self, attrs, htmlfilter):
        """
        Check <embed> start tag.
        """
        self._check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        self._check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)
        if attrs.has_key('src'):
            src = attrs['src']
            if '?' in src:
                i = src.rfind('?')
                src = src[:i]
            if "." in src:
                # prevent CVE-2002-0022
                i = src.rfind('.')
                if len(src[i:]) > 10:
                    msg = "%s %r\n Detected and prevented IE " \
                          "filename overflow crash"
                    wc.log.warn(wc.LOG_FILTER, msg, htmlfilter, src)
                    del attrs['src']

    def fieldset_start (self, attrs, htmlfilter):
        """
        Check <fieldset> start tag.
        """
        if attrs.has_key('style'):
            # prevent Mozilla crash bug on fieldsets
            if "position" in attrs['style']:
                msg = "%s\n Detected and prevented Mozilla "\
                      "<fieldset style> crash bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                del attrs['style']

    def font_start (self, attrs, htmlfilter):
        """
        Check <font> start tag.
        """
        self._check_attr_size(attrs, 'size', htmlfilter)

    def frame_start (self, attrs, htmlfilter):
        """
        Check <frame> start tag.
        """
        self._check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        self._check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)

    def hr_start (self, attrs, htmlfilter):
        """
        Check <hr> start tag.
        """
        # prevent CAN-2003-0469
        self._check_attr_size(attrs, 'align', htmlfilter, maxlen=50)

    def iframe_start (self, attrs, htmlfilter):
        """
        Check <iframe> start tag.
        """
        self._check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        self._check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)

    def img_start (self, attrs, htmlfilter):
        """
        Check <img> start tag.
        """
        # sanitize *src values
        self._check_percent_url(attrs, 'src', htmlfilter)
        self._check_javascript_url(attrs, 'src', htmlfilter)
        self._check_percent_url(attrs, 'lowsrc', htmlfilter)
        self._check_javascript_url(attrs, 'lowsrc', htmlfilter)
        # sanitize width/height values
        self._check_attr_size(attrs, 'width', htmlfilter)
        self._check_attr_size(attrs, 'height', htmlfilter)

    def input_start (self, attrs, htmlfilter):
        """
        Check <input> start tag.
        """
        if attrs.has_key('type'):
            # prevent IE crash bug on empty type attribute
            if not attrs['type']:
                msg = "%s\n Detected and prevented IE <input type> crash bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                del attrs['type']

    def link_start (self, attrs, htmlfilter):
        # CAN-2005-1155 and others
        if attrs.has_key('rel') and attrs.has_key('href'):
            if attrs['rel'].strip().lower() == 'icon':
                self._check_javascript_url(attrs, 'href', htmlfilter)

    def marquee_start (self, attrs, htmlfilter):
        """
        Check <marquee> start tag.
        """
        self._check_attr_size(attrs, 'height', htmlfilter)

    def meta_start (self, attrs, htmlfilter):
        """
        Check <meta> start tag.
        """
        if attrs.has_key('content') and self.macintosh:
            # prevent CVE-2002-0153
            if attrs.get('http-equiv', '').lower() == 'refresh':
                url = attrs['content'].lower()
                if ";" in url:
                    url = url.split(";", 1)[1]
                if url.startswith('url='):
                    url = url[4:]
                if url.startswith('file:/'):
                    msg = "%s %r\n Detected and prevented local file " \
                          "redirection"
                    wc.log.warn(wc.LOG_FILTER, msg, htmlfilter,
                                attrs['content'])
                    del attrs['content']

    def object_start (self, attrs, htmlfilter):
        """
        Check <object> start tag.
        """
        if attrs.has_key('type'):
            # prevent CAN-2003-0344, only one / (slash) allowed
            t = attrs['type']
            c = t.count("/")
            if c > 1:
                msg = "%s\n Detected and prevented IE <object type> bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                t = t.replace("/", "", c-1)
                attrs['type'] = t
        if attrs.has_key('codebase'):
            self.in_winhelp = attrs['codebase'].lower().startswith('hhctrl.ocx')
        # prevent CAN-2004-0380, see http://www.securityfocus.com/bid/9658/
        if attrs.has_key('data'):
            url = wc.url.url_norm(attrs['data'])[0]
            url = urllib.unquote(url)
            if url.startswith('its:') or \
               url.startswith('mk:') or \
               url.startswith('ms-its:') or \
               url.startswith('ms-itss:'):
                # url scheme is vulnerable
                i = url.find('!')
                if i != -1:
                    # url specifies alternate location
                    msg = "%s\n Detected and prevented Microsoft Internet " \
                          "Explorer ITS Protocol Zone Bypass Vulnerability"
                    wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                    attrs['data'] = url[:i]

    def object_end (self):
        """
        Check <object> start tag.
        """
        if self.in_winhelp:
            self.in_winhelp = False

    def param_start (self, attrs, htmlfilter):
        """
        Check <param> start tag.
        """
        if attrs.has_key('value') and self.in_winhelp:
            # prevent CVE-2002-0823
            if len(attrs['value']) > 50:
                msg = "%s\n Detected and prevented WinHlp overflow bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                del attrs['value']

    def table_start (self, attrs, htmlfilter):
        """
        Check <table> start tag.
        """
        if attrs.has_key('width'):
            # prevent CAN-2003-0238, table width=-1 crashes ICQ client
            if attrs['width'] == '-1':
                msg = "%s\n Detected and prevented ICQ table width crash bug"
                wc.log.warn(wc.LOG_FILTER, msg, htmlfilter)
                del attrs['width']
