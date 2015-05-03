# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Test script to test filtering.
"""

import unittest
import os
import wc.configuration
import wc.filter.xmlfilt.XmlFilter
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY
from wc.http.header import WcMessage


class TestXmlRewriter(unittest.TestCase):
    """
    All these tests work with a _default_ filter configuration.
    If you change any of the *.zap filter configs, tests can fail...
    """

    def setUp(self):
        logfile = os.path.join(wc.InstallData, "test", "logging.conf")
        wc.initlog(logfile, filelogs=False)
        wc.configuration.init()
        wc.configuration.config['filters'] = ['XmlRewriter']
        wc.configuration.config.init_filter_modules()
        self.headers = WcMessage()
        self.headers['Content-Type'] = "text/xml"

    def filt(self, data, result, url=""):
        """
        Filter specified data, expect result. Call this only once per test!
        """
        self.attrs = get_filterattrs(url, "localhost",
             [STAGE_RESPONSE_MODIFY], serverheaders=self.headers,
             headers=self.headers)
        filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', self.attrs)
        self.assertEqual(filtered, result)

    def testRdfDescription(self):
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

    def testRdfDescription2(self):
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

    def testRdfDescription3(self):
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
