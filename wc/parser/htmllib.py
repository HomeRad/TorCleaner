"""A parser for HTML"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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

try:
    import htmlop
except ImportError:
    import sys
    sys.stderr.write("""
Could not import the "htmlop" module.
Please run 'python2 setup.py install' to install WebCleaner
completely on your system.
For local installation you can copy the file
build/lib.../htmlop.so into the wc/parser/ directory.
Then you can run 'python2 webcleaner' from the source directory.
""")
    sys.exit(1)

# --------------------------------------------------------------------
# accelerated HTML parser

class HTMLParser:
    # Interface -- initialize and reset this instance
    def __init__(self):
        self.parser = htmlop.parser(self)
        self.feed = self.parser.feed
        self.reset = self.parser.reset
        self.flush = self.parser.flush

    # handlers, can be overridden
    def handle_ref(self, name):
        """This method is called to process a character or entity  reference
        of the form "&ref;" where ref is a general reference.
        """
        pass

    def handle_decl(self, tag, attrs):
        """This method is called to handle tags of the form "<! >".
        """
        pass

    def handle_xmldecl(self, tag, attrs):
        """This method is called to handle tags of the form "<? ?>".
        """
        pass

    def handle_starttag(self, tag, attrs):
        """This method is called to handle start tags of the form "< >".
        Tags of the form "<a/>" are treated as "<a></a>".
        """
        pass

    def handle_endtag(self, tag):
        """This method is called to handle end tags of the form "</ >".
        """
        pass

    def handle_data(self, data):
        """This method is called to process arbitrary data.
        """
        pass

    def handle_comment(self, data):
        """This method is called when a comment is encountered. The comment
        argument is a string containing the text between the "<!--" and "-->"
        delimiters, but not the delimiters themselves.
        """
        pass

if __name__ == '__main__':
    print "Ok"
