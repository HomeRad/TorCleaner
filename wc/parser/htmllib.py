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
    import htmlsax
except ImportError:
    import sys
    sys.stderr.write("""
Could not import the "htmlsax" module.
Please run 'python setup.py install' to install WebCleaner
completely on your system.
For local installation you can copy the file
build/lib.../htmlsax.so into the wc/parser/ directory.
Then you can run 'python webcleaner' from the source directory.
""")
    sys.exit(1)

# --------------------------------------------------------------------
# accelerated HTML parser

class HtmlParser:
    # Interface -- initialize and reset this instance
    def __init__(self):
        self.parser = htmlsax.parser(self)
        self.feed = self.parser.feed
        self.flush = self.parser.flush
        self.reset = self.parser.reset


class HtmlPrinter(HtmlParser):
    """handles all functions by printing the function name and
       attributes"""
    def __getattr__(self, name):
        self.mem = name
        return self._print

    def _print (self, *attrs):
        print self.mem, attrs


def _test():
    p = HtmlPrinter()
    p.flush()

if __name__ == '__main__':
    _test()
