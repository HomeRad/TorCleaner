# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
"""
Filter some security flaws out of HTML tags.

WARNING: this is by no means a complete. Don't rely on this module
to catch all known security flaws!
If you think you found a HTML related security flaw that is not covered
by this module, you are encouraged to inform me with details.
"""

import re
import urllib
from ... import log, LOG_HTML, strformat, url as urlutil


# helper methods to check/sanitize values

def has_lots_of_percents(url):
    """
    Return True iff URL has more than 10 percent chars in a row.
    """
    if not url:
        return False
    return '%'*11 in url


def has_dashes_in_hostname(url):
    """
    Return True iff URL hostname has more than 2 consecutive dashes.
    """
    i = url.find(":")
    if i == -1:
        return False
    if url[:i].lower() in ("javascript",):
        return False
    host = url[i+1:].lstrip("/")
    i = host.find("/")
    if i != -1:
        host = host[:i]
    return "---" in host


def check_javascript_url(attrs, name, htmlfilter):
    """
    Check if url has javascript: embedded.
    """
    if name not in attrs:
        return
    url = attrs.get_true(name, u"").strip().lower()
    # to be sure catch all javascript: stuff
    if "javascript:" in url:
        msg = "%s\n Detected and prevented invalid JS URL reference"
        log.info(LOG_HTML, msg, htmlfilter)
        del attrs[name]

isfloat = re.compile(r"^[1-9][0-9]*\.[0-9]+$").search

def check_length(attrs, name, htmlfilter, maxlen=4):
    """
    Check correct format of a length attribute. Allowed are
    digits, followed by 'px', 'em' or '%'.
    Floating point numbers are converted to integers before checking.
    Too long and invalid values will be removed.
    Side effect: attribute value is stripped from whitespace.
    """
    value = attrs.get_true(name, u"")
    if not value:
        return
    # Assume that if we want a specific length whitespace is not
    # allowed in the attribute value.
    value = value.strip()
    # some sites have a double percent
    if value.endswith('%%'):
        value = value[:-1]
    attrs[name] = value
    # check value
    tvalue = value.lower()
    if tvalue[-2:] in ('px', 'em'):
        tvalue = tvalue[:-2]
    elif tvalue.endswith('%'):
        tvalue = tvalue[:-1]
    if isfloat(tvalue):
        try:
            tvalue = str(int(float(tvalue)))
        except StandardError:
            pass
    if not tvalue.isdigit() or len(tvalue) > maxlen:
        msg = "%s\n Detected invalid length format %r"
        log.info(LOG_HTML, msg, htmlfilter, value)
        del attrs[name]


def check_attr_size(attrs, name, htmlfilter, maxlen=4):
    """
    Sanitize too large values (usually used for length attributes).
    Side effect: attribute value is stripped from whitespace.
    """
    if name not in attrs:
        return
    # Note that a maxlen of 4 is recommended to also allow
    # percentages like '100%'.
    val = attrs.get_true(name, u"").lower()
    if len(val) > maxlen:
        msg = "%s %r\n Detected a too large %s attribute value"
        msg += " (length %d > %d)" % (len(val), maxlen)
        log.info(LOG_HTML, msg, htmlfilter, val, name)
        del attrs[name]


def check_attr_number(attrs, htmlfilter, maxnum=200):
    """
    Restrict the number of attributes a start tag can have. Too much attributes
    are known to crash some browsers.
    """
    l = len(attrs)
    if l > maxnum:
        msg = "%s\n  Too much attributes (%d > %d) in tag"
        log.info(LOG_HTML, msg, htmlfilter, l, maxnum)
        attrs.popitem()
        while len(attrs) > maxnum:
            attrs.popitem()


def check_url(attrs, name, htmlfilter):
    """
    Check if url has suspicious patterns.
    """
    if name not in attrs:
        return
    url = attrs.get_true(name, u"")
    if has_lots_of_percents(url):
        # prevent CAN-2003-0870
        msg = "%s %r\n Detected and prevented Opera percent " \
              "encoding overflow crash"
        log.info(LOG_HTML, msg, htmlfilter, url)
        del attrs[name]
    if has_dashes_in_hostname(url):
        # prevent firefox crash
        msg = "%s %r\n Detected and prevented Firefox " \
              "dashes-in-hostname overflow crash"
        log.info(LOG_HTML, msg, htmlfilter, url)
        del attrs[name]


# security checker

class HtmlSecurity(object):
    """
    Scan and repair known security exploits in HTML start/end tags.
    """

    def __init__(self):
        # inside object tag calling WinHelp
        self.in_winhelp = False
        # number of nested <object> levels
        self.object_level = 0

    # scan methods

    def scan_start_tag(self, tag, attrs, htmlfilter):
        """
        Delegate to individual start tag handlers.
        """
        assert strformat.is_ascii(tag)
        check_attr_number(attrs, htmlfilter)
        fun = "%s_start" % tag
        if hasattr(self, fun):
            if getattr(self, fun)(attrs, htmlfilter):
                return True
        # generic length checking
        check_length(attrs, 'width', htmlfilter)
        check_length(attrs, 'height', htmlfilter)

    def scan_end_tag(self, tag):
        """
        Delegate to individual end tag handlers.
        """
        assert strformat.is_ascii(tag)
        fun = "%s_end" % tag
        if hasattr(self, fun):
            getattr(self, fun)()

    # tag specific scan methods, sorted alphabetically

    def a_start(self, attrs, htmlfilter):
        """
        Check <a> start tag.
        """
        check_url(attrs, 'href', htmlfilter)

    def applet_start(self, attrs, htmlfilter):
        """
        Check <applet> start tag.
        """
        check_length(attrs, 'hspace', htmlfilter)

    def body_start(self, attrs, htmlfilter):
        """
        Check <body> start tag.
        """
        onload = attrs.get_true(u"onload", u"")
        if not onload:
            return
        pattern = r"window\s*\(\s*\)"
        if re.compile(pattern).search(onload):
            del attrs['onload']
            msg = "%s\n Detected and prevented IE window() crash bug"
            log.info(LOG_HTML, msg, htmlfilter)

    def embed_start(self, attrs, htmlfilter):
        """
        Check <embed> start tag.
        """
        check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)
        src = attrs.get_true(u"src", u"")
        if not src:
            return
        i = src.find('?')
        if i != -1:
            src = src[:i]
        i = src.rfind('.')
        if i != -1:
            # prevent CVE-2002-0022
            j = src.rfind('/')
            if i > j and len(src[i:]) > 10:
                msg = "%s %r\n Detected and prevented IE " \
                      "filename overflow crash"
                log.info(LOG_HTML, msg, htmlfilter, src)
                del attrs['src']

    def fieldset_start(self, attrs, htmlfilter):
        """
        Check <fieldset> start tag.
        """
        # prevent Mozilla crash bug on fieldsets
        if "position" in attrs.get_true("style", u""):
            msg = "%s\n Detected and prevented Mozilla "\
                  "<fieldset style> crash bug"
            log.info(LOG_HTML, msg, htmlfilter)
            del attrs['style']

    def font_start(self, attrs, htmlfilter):
        """
        Check <font> start tag.
        """
        check_attr_size(attrs, 'size', htmlfilter)

    def frame_start(self, attrs, htmlfilter):
        """
        Check <frame> start tag.
        """
        check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)

    def hr_start(self, attrs, htmlfilter):
        """
        Check <hr> start tag.
        """
        # prevent CAN-2003-0469
        check_attr_size(attrs, 'align', htmlfilter, maxlen=50)

    def iframe_start(self, attrs, htmlfilter):
        """
        Check <iframe> start tag.
        """
        check_attr_size(attrs, 'src', htmlfilter, maxlen=1024)
        check_attr_size(attrs, 'name', htmlfilter, maxlen=1024)
        check_url(attrs, 'src', htmlfilter)

    def img_start(self, attrs, htmlfilter):
        """
        Check <img> start tag.
        """
        # sanitize *src values
        check_url(attrs, 'src', htmlfilter)
        check_javascript_url(attrs, 'src', htmlfilter)
        check_url(attrs, 'lowsrc', htmlfilter)
        check_javascript_url(attrs, 'lowsrc', htmlfilter)

    def input_start(self, attrs, htmlfilter):
        """
        Check <input> start tag.
        """
        if 'type' in attrs and not attrs['type']:
            # prevent IE crash bug on empty type attribute
            msg = "%s\n Detected and prevented IE <input type> crash bug"
            log.info(LOG_HTML, msg, htmlfilter)
            del attrs['type']

    def link_start(self, attrs, htmlfilter):
        # CAN-2005-1155 and others
        if 'rel' in attrs and 'href' in attrs:
            if attrs.get_true('rel', u"").strip().lower() == 'icon':
                check_javascript_url(attrs, 'href', htmlfilter)

    def meta_start(self, attrs, htmlfilter):
        """
        Check <meta> start tag.
        """
        if 'content' in attrs:
            # prevent redirect to non-http/ftp file
            refresh = attrs.get_true('name', u"")
            refresh = attrs.get_true('http-equiv', refresh)
            if refresh.lower() == 'refresh':
                # lowercase and strip all whitespace
                url = attrs.get_true('content', u"").lower()
                url = strformat.stripall(url)
                # content can be "1;url=http://;url=javascript:alert('boo')"
                # so be sure to check all urls
                for url in url.split(";url="):
                    url = strformat.unquote(url, matching=True)
                    url_ok = url.startswith(("http://", "https://", "ftp://"))
                    if not url_ok and ":" in url:
                        msg = "%s %r\n Detected invalid redirection."
                        log.info(LOG_HTML, msg, htmlfilter, attrs['content'])
                        del attrs['content']
                        break

    def object_start(self, attrs, htmlfilter):
        """
        Check <object> start tag.
        """
        if self.object_level == 3:
            # Prevent IE crash; see http://secunia.com/advisories/19762/
            return True
        self.object_level += 1
        if 'type' in attrs:
            # prevent CAN-2003-0344, only one / (slash) allowed
            t = attrs.get_true('type', u"")
            c = t.count("/")
            if c > 1:
                msg = "%s\n Detected and prevented IE <object type> bug"
                log.info(LOG_HTML, msg, htmlfilter)
                t = t.replace("/", "", c-1)
                attrs['type'] = t
        if 'codebase' in attrs:
            self.in_winhelp = attrs.get_true('codebase', u"").lower().startswith('hhctrl.ocx')
        # prevent CAN-2004-0380, see http://www.securityfocus.com/bid/9658/
        if 'data' in attrs:
            url = urlutil.url_norm(attrs.get_true('data', u""))[0]
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
                    log.info(LOG_HTML, msg, htmlfilter)
                    attrs['data'] = url[:i]
        if 'classid' in attrs:
            classid = attrs.get_true('classid', u"").upper()
            if 'EC444CB6-3E7E-4865-B1C3-0DE72EF39B3F' in classid:
                msg = "Detected IE msdds.dll overflow attack."
                log.info(LOG_HTML, msg, htmlfilter)
                del attrs['classid']

    def object_end(self):
        """
        Check <object> start tag.
        """
        if self.object_level > 1:
            self.object_level -= 1
        if self.in_winhelp:
            self.in_winhelp = False

    def param_start(self, attrs, htmlfilter):
        """
        Check <param> start tag.
        """
        if 'value' in attrs and self.in_winhelp:
            # prevent CVE-2002-0823
            if len(attrs.get_true('value', u"")) > 50:
                msg = "%s\n Detected and prevented WinHlp overflow bug"
                log.info(LOG_HTML, msg, htmlfilter)
                del attrs['value']

    def table_start(self, attrs, htmlfilter):
        """
        Check <table> start tag.
        """
        if 'width' in attrs:
            # prevent CAN-2003-0238, table width=-1 crashes ICQ client
            if attrs['width'] == '-1':
                msg = "%s\n Detected and prevented ICQ table width crash bug"
                log.info(LOG_HTML, msg, htmlfilter)
                del attrs['width']
