#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
import sys
sys.stderr = sys.stdout
from wc.js import jslib, JSListener

class JSOutputter(JSListener.JSListener):
    def jsProcessData (self, data):
        print "data", data

    def jsProcessPopup (self):
        print "popup"

    def jsProcessError (self, err):
        print err

out = JSOutputter()
jsEnv = jslib.JSEnv()
jsEnv.listeners.append(out)
# popups
jsEnv.executeScript("window.open('')", 1.1)
jsEnv.executeScript("eval('window.open(\\'\\')')", 1.1)
# document.write
jsEnv.executeScript("""
a='ht'
b='ml'
document.write('<'+a+b+'>')""", 1.1)
# reference error
jsEnv.executeScript("ä", 1.1)
# syntax error
jsEnv.executeScript("a='", 1.5)
jsEnv.listeners.remove(out)
jsEnv = None
