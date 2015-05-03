# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005 Joe Wreschnig
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test HTML file syntax.
"""

import unittest
import urllib
import HTMLParser
import os
import sys
import glob
import wc.fileutil
import wc.decorators
from tests import has_proxy
from nose import SkipTest


htmlfiles = None
def get_htmlfiles():
    """
    Find all .po files in this source.
    """
    global htmlfiles
    if htmlfiles is None:
        htmlfiles = []
        htmlfiles.extend(wc.fileutil.rglob("templates", "*.html"))
        htmlfiles.extend(wc.fileutil.rglob("doc/en", "*.html"))
    return htmlfiles


def parse_html(url):
    """
    Parse HTML url.
    @raise HTMLParser.HTMLParseError
    """
    fp = urllib.urlopen(url)
    html_parser = HTMLParser.HTMLParser()
    try:
        html_parser.feed(fp.read())
    finally:
        fp.close()


class CheckHtml(unittest.TestCase):

    def check_html(self, url):
        try:
            parse_html(url)
        except HTMLParser.HTMLParseError:
            exc = sys.exc_info()[1]
            msg = "%s:%d:%d: %s" % (url, exc.lineno, exc.offset, exc.msg)
            self.fail(msg)


class TestHtml(CheckHtml):
    """Test HTMl file syntax."""

    def test_html(self):
        """
        Test HTML files syntax.
        """
        for f in get_htmlfiles():
            self.check_html(f)


class TestProxyHtml(CheckHtml):
    """Test proxy HTML file syntax."""

    def test_html(self):
        if not has_proxy():
            raise SkipTest()
        for name in glob.glob("templates/classic/*.html"):
            name = os.path.basename(name)
            url = "http://localhost:8081/%s" % name
            self.check_html(url)
            self.check_html(url+".de")
            self.check_html(url+".en")
        # check error page
        self.check_html("http://localhost:8081/hulla")
