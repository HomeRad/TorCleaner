#!/usr/bin/python
from wc.js import jslib, JSListener
import sys
sys.stderr = sys.stdout

class JSOutputter(JSListener.JSListener):
    def jsProcessData (self, data):
        print "data", data

    def jsProcessPopup (self):
        print "popup"

    def jsProcessError (self, err):
        print err

out = JSOutputter()
jsEnv = jslib.new_jsenv()
jsEnv.attachListener(out)
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
jsEnv.detachListener(out)
