# -*- coding: iso-8859-1 -*-
import unittest
from wc.url import url_norm, url_quote, is_valid_url, is_valid_js_url
from tests import StandardTest


class TestUrl (StandardTest):

    def testUrl (self):
        url = "http://server/..%5c..%5c..%5c..%5c..%5c..%5..%5c..%5ccskin.zip"
        nurl = url_quote(url_norm(url))
        self.assertEquals(nurl, "http://server/cskin.zip")
        url = "http://groups.google.com/groups?hl=en&lr=&ie=UTF-8&threadm=3845B54D.E546F9BD%40monmouth.com&rnum=2&prev=/groups%3Fq%3Dlogitech%2Bwingman%2Bextreme%2Bdigital%2B3d%26hl%3Den%26lr%3D%26ie%3DUTF-8%26selm%3D3845B54D.E546F9BD%2540monmouth.com%26rnum%3D2"
        nurl = url_quote(url_norm(url))
        self.assertEqual(url, nurl)

    def testValid (self):
        self.assert_(is_valid_url("http://www.imadoofus.com"))
        self.assert_(is_valid_url("http://www.imadoofus.com/"))
        self.assert_(is_valid_url("http://www.imadoofus.com/~calvin"))
        self.assert_(is_valid_url("http://www.imadoofus.com/a,b"))
        self.assert_(is_valid_url("http://www.imadoofus.com#anchor55"))
        self.assert_(is_valid_js_url("http://www.imadoofus.com/?hulla=do"))


if __name__ == '__main__':
    unittest.main(defaultTest='TestUrl')
else:
    suite = unittest.makeSuite(TestUrl, 'test')
