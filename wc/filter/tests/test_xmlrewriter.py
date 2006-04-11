# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2006 Bastian Kleineidam
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
Test script to test filtering.
"""

import unittest
import os
import tests
import wc
import wc.configuration
import wc.filter.xmlfilt.XmlFilter
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY
from wc.http.header import WcMessage


class TestXmlRewriter (tests.StandardTest):
    """
    All these tests work with a _default_ filter configuration.
    If you change any of the *.zap filter configs, tests can fail...
    """

    def setUp (self):
        logfile = os.path.join(wc.InstallData, "test", "logging.conf")
        wc.initlog(logfile, filelogs=False)
        wc.configuration.init()
        wc.configuration.config['filters'] = ['XmlRewriter']
        wc.configuration.config.init_filter_modules()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/xml"

    def filt (self, data, result, url=""):
        """
        Filter specified data, expect result. Call this only once per test!
        """
        self.attrs = get_filterattrs(url, "localhost",
             [STAGE_RESPONSE_MODIFY], serverheaders=self.headers,
             headers=self.headers)
        filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', self.attrs)
        self.assertEqual(filtered, result)

    def testRdfDescription (self):
        self.filt("""<?xml version="1.0" encoding="ISO-8859-1"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description>bla &lt;a href='http://fmads.osdn.com/cgi-bin/adlog.pl?index,tkgk0128en'&gt;&lt;/a&gt;</description>
</item>
</rdf:RDF>""",
                  """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description><![CDATA[bla ]]></description>
</item>
</rdf:RDF>""")

    def testRdfDescription2 (self):
        self.filt("""<?xml version="1.0" encoding="ISO-8859-1"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description>bla &lt;foo&gt;</description>
</item>
</rdf:RDF>""",
                  """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description><![CDATA[bla ]]></description>
</item>
</rdf:RDF>""")

    def testRdfDescription3 (self):
        self.filt("""<?xml version="1.0" encoding="ISO-8859-1"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description>bla &lt;img grog='warz'&gt;</description>
</item>
</rdf:RDF>""",
                  """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/">
<item rdf:about="blubb">
<description><![CDATA[bla <img>]]></description>
</item>
</rdf:RDF>""")


def test_suite ():
    return unittest.makeSuite(TestXmlRewriter)


if __name__ == '__main__':
    unittest.main()
