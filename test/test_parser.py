#!/usr/bin/env python2

from wc.parser.htmllib import HTMLParser

class HTMLPrinter(HTMLParser):
    """HTML debug printer"""
    def __init__(self, name):
        HTMLParser.__init__(self)
        self._name = name

    def handle_ref(self, name):
        print self._name, "ref", `name`

    def handle_decl(self, name, attrs):
        print self._name, "decl", `name`, attrs

    def handle_xmldecl(self, name, attrs):
        print self._name, "xmldecl", `name`, attrs

    def handle_data(self, data):
        print self._name, "data", `data`

    def handle_comment(self, data):
        print self._name, "comment", `data`

    def handle_starttag(self, tag, attrs):
        print self._name, "starttag", `tag`, attrs

    def handle_endtag(self, tag):
        print self._name, "endtag", `tag`


tests = (
    # start tags
    """<a b="c">""",
    """<a b='c'>""",
    """<a b=c">""",
    """<a b="c>""",
    """<a b=>""",
    """<a =c>""",
    """<a =>""",
    """<a >""",
    """< a>""",
    """< a >""",
    """<>""",
    """< >""",
    # more start tags
    """<a b=c"><a b="c">""",
    """<a b="c><a b="c">""",
    # comments
    """<!---->""",
    """<!----->""",
    """<!------>""",
    """<!------->""",
    """<!---- >""",
    """<!-- -->""",
    """<!-- -- >""",
    """<!---- />-->""",
    # end tags
    """</br>""",
    """</ br>""",
    """</ br >""",
    """</br >""",
    """< / br>""", # invalid (is start tag)
    """< /br>""", # invalid (is start tag)
    # start and end tag
    """<br/>""",
    # declaration tags
    """<!DOCTYPE adrbook SYSTEM "adrbook.dtd">""",
    # misc
    """<?xml version="1.0" encoding="latin1"?>""",

)

flushtests = (
    "<",
    "<a",
)

p = HTMLPrinter("p")
for t in tests:
    print "HTML", `t`
    p.feed(t)
print "subsequent interwoven parsing"
p1 = HTMLPrinter("p1")
p.feed("<")
p1.feed("<")
p.feed("ht")
p1.feed("ht")
p.feed("ml")
p1.feed("ml")
p.feed(">")
p1.feed(">")

print "reset test"
p.feed("<")
p.reset()
p.feed(">")

print "flush tests"
for t in flushtests:
    p.reset()
    p.feed(t)
    p.flush()
