# -*- coding: iso-8859-1 -*-
import unittest
import wc.url
import StandardTest


class TestUrl (StandardTest.StandardTest):

    def testUrlPathAttack (self):
        url = "http://server/..%5c..%5c..%5c..%5c..%5c..%5..%5c..%5ccskin.zip"
        nurl = "http://server/cskin.zip"
        self.assertEquals(wc.url.url_quote(wc.url.url_norm(url)), nurl)

    def testUrlQuoting (self):
        url = "http://groups.google.com/groups?hl=en&lr=&ie=UTF-8&threadm=3845B54D.E546F9BD%40monmouth.com&rnum=2&prev=/groups%3Fq%3Dlogitech%2Bwingman%2Bextreme%2Bdigital%2B3d%26hl%3Den%26lr%3D%26ie%3DUTF-8%26selm%3D3845B54D.E546F9BD%2540monmouth.com%26rnum%3D2"
        nurl = url
        self.assertEqual(wc.url.url_quote(wc.url.url_norm(url)), nurl)

    def testUrlFixing (self):
        url = r"http://groups.google.com\test.html"
        nurl = "http://groups.google.com/test.html"
        self.assertEqual(wc.url.url_norm(url), nurl)
        url = r"http://groups.google.com/a\test.html"
        nurl = "http://groups.google.com/a/test.html"
        self.assertEqual(wc.url.url_norm(url), nurl)
        url = r"http://groups.google.com\a\test.html"
        nurl = "http://groups.google.com/a/test.html"
        self.assertEqual(wc.url.url_norm(url), nurl)
        url = r"http://groups.google.com\a/test.html"
        nurl = "http://groups.google.com/a/test.html"
        self.assertEqual(wc.url.url_norm(url), nurl)

    def testValid (self):
        self.assert_(wc.url.is_valid_url("http://www.imadoofus.com"))
        self.assert_(wc.url.is_valid_url("http://www.imadoofus.com/"))
        self.assert_(wc.url.is_valid_url("http://www.imadoofus.com/~calvin"))
        self.assert_(wc.url.is_valid_url("http://www.imadoofus.com/a,b"))
        self.assert_(wc.url.is_valid_url("http://www.imadoofus.com#anchor55"))
        self.assert_(wc.url.is_valid_js_url("http://www.imadoofus.com/?hulla=do"))


if __name__ == '__main__':
    unittest.main(defaultTest='TestUrl')
else:
    suite = unittest.makeSuite(TestUrl, 'test')
