#!/usr/bin/env python
"""A parser for SGML"""

# XXX This only supports those SGML features used by HTML.

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char and entity references and end tags are special)
# and CDATA (character data -- only end tags are special).

# sgmlop support added by fredrik@pythonware.com (April 6, 1998)

import sys

try:
    import sgmlop
except ImportError:
    sys.stderr.write("""
Please run 'python2 setup.py build_ext' and copy the file
build/lib.../sgmlop.so into the wc/parser/ directory.
Then you can run 'python2 webcleaner' from the source directory
webcleaner-x.x/.
""")
    sys.exit(1)

# --------------------------------------------------------------------
# accelerated SGML parser

class SGMLParser:
    # Interface -- initialize and reset this instance
    def __init__(self):
        self.parser = sgmlop.SGMLParser(self)
        self.feed = self.parser.feed
        self.reset = self.parser.reset

    # XXX For derived classes only -- enter literal mode (CDATA) till EOF
    def setnomoretags(self):
        pass

    # XXX For derived classes only -- enter literal mode (CDATA)
    def setliteral(self, *args):
        pass

    # Interface -- handle the remaining data
    def close(self):
        try:
            self.parser.close()
        finally:
            self.parser = None

    # handlers, can be overridden
    def handle_entityref(self, name): pass
    def handle_charref(self, name):   pass
    def handle_proc(self, name):      pass
    def handle_special(self, name):   pass
    def handle_data(self, data):      pass
    def handle_cdata(self, data):     pass
    def handle_comment(self, data):   pass
    def unknown_starttag(self, tag, attrs): pass
    def unknown_endtag(self, tag):    pass
    def unknown_charref(self, ref):   pass
    def unknown_entityref(self, ref): pass

if __name__ == '__main__':
    print "Ok"
