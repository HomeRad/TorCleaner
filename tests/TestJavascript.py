#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""test script to test JavaScript engine"""

import unittest
from wc.js import jslib, JSListener


class JSTester (JSListener.JSListener):
    """JavaScript engine event listener"""
    def __init__ (self):
        self.data = ""
        self.popups = 0
        self.err = ""


    def jsProcessData (self, data):
        self.data += data


    def jsProcessPopup (self):
        self.popups += 1


    def jsProcessError (self, err):
        self.err = err


class TestJavascript (unittest.TestCase):
    def setUp (self):
        self.out = JSTester()
        self.jsEnv = jslib.JSEnv()
        self.jsEnv.listeners.append(self.out)


    def testPopups (self):
        """test popup counting"""
        self.jsEnv.executeScript("window.open('')", 1.1)
        self.jsEnv.executeScript("eval('window.open(\\'\\')')", 1.1)
        self.assert_(self.out.popups==2)


    def testDocumentWrite (self):
        """document.write() function"""
        self.jsEnv.executeScript("""
a='ht'
b='ml'
document.write('<'+a+b+'>')""", 1.1)
        self.assert_(self.out.data=="<html>")


    def testReferenceError (self):
        """test provoked reference error"""
        self.jsEnv.executeScript("ä", 1.1)
        self.assert_(self.out.err.startswith("ReferenceError:"))


    def testSyntaxError (self):
        """test provoked syntax error"""
        self.jsEnv.executeScript("a='", 1.5)
        self.assert_(self.out.err.startswith("SyntaxError:"))


    def tearDown (self):
        """remove js engine listener"""
        self.jsEnv.listeners.remove(self.out)
        self.jsEnv = None


if __name__ == '__main__':
    unittest.main()
else:
    suite = unittest.makeSuite(TestJavascript, 'test')
